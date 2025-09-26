import streamlit as st
import math
import random
from datetime import datetime
from html import escape
import pandas as pd
import numpy as np
from ataques_shoji import ataque_armado as aa
# ---------------------------
# Configuração da página
# ---------------------------
st.set_page_config(page_title="Ficha Shoji Yoshiro", layout="wide")

st.markdown("""
<style>
.big-num{font-size:2.4rem;font-weight:800;line-height:1;margin:.15rem 0 .35rem 0}
.pill{display:inline-block;padding:.15rem .55rem;border:1px solid rgba(255,255,255,.18);
      border-radius:999px;margin:.15rem .25rem 0 0;background:rgba(255,255,255,.04)}
.die{display:inline-block;font-weight:700;padding:.15rem .45rem;border-radius:.5rem;
     border:1px dashed rgba(255,255,255,.18);margin:.15rem .2rem 0 0}
.sec-label{opacity:.8;font-size:.9rem;margin-top:.25rem}
</style>
""", unsafe_allow_html=True)

def rolar_pericia(nome: str, total: int) -> dict:
    """Rola 1d20 + total para teste de perícia."""
    d20 = random.randint(1, 20)
    return {
        "Habilidade": f"Perícia – {nome}",
        "Rolagens": [d20],            # mostra o d20
        "Ataque": d20 + int(total),   # 'show_result' exibe como Ataque/Teste
    }

def pericias_ui(df):
    st.subheader('Tabela Perícias')

    col_pericia = "Perícia" if "Perícia" in df.columns else "Pericia"

    # divide o df igualmente em 2 blocos
    n = len(df)
    mid = (n + 1) // 2
    bloco_esq = df.iloc[:mid].reset_index(drop=True)
    bloco_dir = df.iloc[mid:].reset_index(drop=True)

    col_esq, col_dir = st.columns(2, gap="large")

    def render_bloco(container, bloco_df, bloco_tag):
        with container:
            # Cabeçalho visual
            h1, h2, h3 = st.columns([3, 2, 1])
            h1.markdown("**Perícia**")
            h2.markdown("**Atributo**")
            h3.markdown("**Total**")

            # Linhas com botão no Total
            for i, row in bloco_df[[col_pericia, "Atributo", "Total"]].iterrows():
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(row[col_pericia])
                c2.write(row["Atributo"])
                key = f"roll_skill_{bloco_tag}_{i}_{row[col_pericia]}"
                if c3.button(str(row["Total"]), key=key, use_container_width=True):
                    st.session_state["skill_last_output"] = (
                        f"Perícia: {row[col_pericia]}",
                        rolar_pericia(row[col_pericia], int(row["Total"]))
                    )

    render_bloco(col_esq, bloco_esq, "L")
    render_bloco(col_dir, bloco_dir, "R")

# ---------------------------
# Utilitários
# ---------------------------

def dado(faces: int, vezes: int = 1) -> list[int]:
    """Rola 'vezes' dados de 'faces' e retorna a lista com os resultados."""
    return [random.randint(1, faces) for _ in range(vezes)]

def dado_cura_aprimorada(faces: int, vezes: int = 1) -> list[int]:
    return [random.randint(3, faces) for _ in range(vezes)]

def mod(atr: int) -> int:
    """Modificador de atributo: floor((atributo-10)/2)."""
    return (atr - 10) // 2

def add_log(msg: str, payload: dict):
    """Salva o resultado no histórico da sessão."""
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.insert(0, {"msg": msg, "payload": payload, "ts": datetime.now().strftime("%H:%M:%S")})

def _pills(items):
    if not items: return ""
    html = "".join(f'<span class="pill">{escape(str(i))}</span>' for i in items)
    return f"<div>{html}</div>"

def _dice_pills(rolls):
    if not rolls: return ""
    html = "".join(f'<span class="die">{escape(str(r))}</span>' for r in rolls)
    return f"<div>{html}</div>"

def _find_numeric_by_keywords(data: dict, keywords: tuple[str, ...]):
    """Procura um valor numérico por palavra-chave no nome da chave."""
    for k, v in data.items():
        if isinstance(v, (int, float)):
            kl = k.lower()
            for kw in keywords:
                if kw in kl:
                    return k, v  # retorna a chave original e o valor
    return None, None

def show_result(title: str, data: dict):
    """Render amigável: decide o 'Resultado' de forma robusta."""
    # 1) tenta pegar "dano"/"cura" em qualquer variação do nome
    key, val = _find_numeric_by_keywords(data, ("dano", "cura"))

    if key is not None:
        primary_label = "Dano" if "dano" in key.lower() else "Cura"
        primary_value = val
    else:
        # 2) fallback: soma rolagens + mods/bônus numéricos, se existirem
        rolls = data.get("Rolagens") or data.get("rolagens") or []
        total = sum(r for r in rolls if isinstance(r, (int, float)))

        # procura campos numéricos que sejam modificadores/bônus
        bonus = 0
        for k, v in data.items():
            if isinstance(v, (int, float)):
                kl = k.lower()
                if "mod" in kl or "bônus" in kl or "bonus" in kl:
                    bonus += v

        if rolls:
            primary_label = "Resultado"
            primary_value = total + bonus
        else:
            # 3) último recurso: mostra ataque/CD ou "-"
            primary_label = "Resultado"
            primary_value = (
                data.get("Rolagem Acerto")
                or data.get("Ataque")
                or data.get("Acerto")
                or data.get("Rolagem de Ataque")
                or data.get("CD")
                or "-"
            )

    alcance = data.get("Alcance") or data.get("alcance")
    efeito  = data.get("Efeito") or data.get("efeito")
    rolls   = data.get("Rolagens") or data.get("rolagens") or []

    with st.container(border=True):
        st.markdown(f"### {title}")


        descricao = (
            data.get("Descrição") or data.get("Descricao") or
            data.get("descrição") or data.get("descricao")
        )
        if descricao:
            st.markdown(f"<p style='opacity:.85'>{escape(str(descricao))}</p>", unsafe_allow_html=True)

        left, right = st.columns([2, 1])

        with left:
            st.markdown(f'<div class="sec-label">{escape(primary_label)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="big-num">{escape(str(primary_value))}</div>', unsafe_allow_html=True)

            if rolls:
                st.caption("Rolagens")
                st.markdown(_dice_pills(rolls), unsafe_allow_html=True)

            chips = []
            if alcance: chips.append(f"Alcance: {alcance}")
            if efeito:  chips.append(f"Efeito: {efeito}")
            if chips:
                st.markdown(_pills(chips), unsafe_allow_html=True)

        with right:
            atk_total = data.get("Rolagem de Ataque") or data.get("Ataque") or data.get("Acerto")
            cd_tr     = data.get("CD do TR") or data.get("CD")
            if atk_total is not None:
                st.metric("Rolagem Total", atk_total)
            if cd_tr is not None:
                st.metric("CD do TR", cd_tr)

    add_log(title, data)

# Utilitários rolagens shoji


def _rola_extras(faces: int, n: int = 1):
    # usa sua função dado(...) se existir; senão, usa random
    if 'dado' in globals():
        return dado(faces, n)  # sua assinatura parece ser dado(faces, quant)
    import random
    return [random.randint(1, faces) for _ in range(n)]

def _add_bonus_ataque(res: dict, bonus: int):
    # suas armas às vezes retornam "Rolagem de Ataque" ou "Ataque"
    if "Rolagem de Ataque" in res:
        res["Rolagem de Ataque"] = int(res["Rolagem de Ataque"]) + int(bonus)
    else:
        res["Ataque"] = int(res.get("Ataque", 0)) + int(bonus)

def _append_rolagens(res: dict, novas_rols: list[int]):
    if not novas_rols:
        return
    if "Rolagens" in res and isinstance(res["Rolagens"], list):
        res["Rolagens"].extend(novas_rols)
    else:
        res["Rolagens"] = list(novas_rols)

# ---------------------------
# FICHA (base do usuário)
# ---------------------------
# Ficha
nivel = 6

# Atributos
For = 20
Des = 7
Con = 18
Int = 14
Sab = 14
Car = 8

#Calcula Maestria =Int(SOMA(1+ARREDONDAR.PARA.CIMA(nivel/4)))
maestria = math.ceil(1 + nivel/4)

# calcula valor do atributo
def mod(atr: int) -> int:
    return (atr - 10) // 2

# Classe de Armadura
CA_Natural = 10 
Uniforme = 8
Escudo = 0
Outros = 10
CA = (CA_Natural+Uniforme+Escudo+Outros) # mod des n aplicavel

# Pontos de Vida - Manual; Pontos de energia =5*nivel+N(mod sab)
PV = 99
PE = 39
PE_maximo_armazenado = 70
cd_do_tr = 10 + maestria + mod(Int) + 1 # não aplicável

# ---------------------------
# Habilidades (coringas)
# ---------------------------

# Estilo oculto adiciona o valor tanto em dano quanto na rolagem de ataque
estilo_oculto = ['Nenhum','1º Fluxo','2º Fluxo', '3º Fluxo', '4º Fluxo', '5º Fluxo', '6º Fluxo', '7º Fluxo', '8º Fluxo', '9º Fluxo', '10ºFluxo']
adicional_estilo_oculto = {
     'Nenhum': 0,
     '1º Fluxo': 1,
     '2º Fluxo': 2,
     '3º Fluxo': 3, 
     '4º Fluxo': 4, 
     '5º Fluxo': 5, 
     '6º Fluxo': 6, 
     '7º Fluxo': 7, 
     '8º Fluxo': 8, 
     '9º Fluxo': 9, 
     '10ºFluxo': 10,
}
posturas = ['Nenhuma','Postura do Sol']
# Nenhuma n faz nada
#postura do sol adiciona mais um dado de dano e +2 no acerto
postura_do_sol = {
     "Acerto": 2,
     "Dano": 1234, #Precisa pegar qual o dado de dano da arma (mudar)
}
armas = [
'Espada Gancho (G 4)',
'Espada Dupla (G 4)',
'Espada Colossal (G 4)',
'Nunchako Pesado (G 4)',
'Lança Grande (G 4)',
'Machado Grande (G 4)',
'Foice Grande (G 4) Afiada',
'Soqueira (G 4)(Aç.B. TP 6m 1PE)',
'Cardume de Adagas (G 3)',
'Adaga de Aparar (G 4)',
]

cast_arma_escolhida = {
     'Espada Gancho (G 4)': aa.espada_gancho,
     'Espada Dupla (G 4)': aa.espada_dupla,
     'Espada Colossal (G 4)': aa.espada_colossal,
     'Nunchako Pesado (G 4)': aa.nunchako_pesado,
     'Lança Grande (G 4)': aa.lanca_grande,
     'Machado Grande (G 4)': aa.machado_grande,
     'Foice Grande (G 4) Afiada': aa.foice_grande,
     'Soqueira (G 4)(Aç.B. TP 6m 1PE)': aa.soqueira,
     'Cardume de Adagas (G 3)': aa.cardume_de_adagas,
     'Adaga de Aparar (G 4)': aa.adaga_de_aparar,
}

arma_dano_faces = {
    'Espada Gancho (G 4)': 8,    # no seu código da espada gancho, vi d8
    'Espada Dupla (G 4)': 8,
    'Espada Colossal (G 4)': 12,
    'Nunchako Pesado (G 4)': 6,
    'Lança Grande (G 4)': 10,
    'Machado Grande (G 4)': 12,
    'Foice Grande (G 4) Afiada': 10,
    'Soqueira (G 4)(Aç.B. TP 6m 1PE)': 4,
    'Cardume de Adagas (G 3)': 4,
    'Adaga de Aparar (G 4)': 4,
}

def cast_ataque_armado():
    arma = arma_atual
    postura = postura_atual
    estilo = estilo_oculto_atual

    # 1) bônus do estilo oculto (mesmo valor em ataque e dano)
    bonus_estilo = adicional_estilo_oculto.get(estilo, 0)
    bonus_ataque = bonus_estilo
    bonus_dano_flat = bonus_estilo

    # 2) postura
    dados_extras = 0
    if postura == 'Postura do Sol':
        bonus_ataque += 2
        dados_extras = 1  # +1 dado do mesmo tipo da arma

    # 3) executa o ataque base da arma
    func = cast_arma_escolhida.get(arma)
    if not func:
        raise ValueError(f"Arma desconhecida: {arma}")
    res = func()  # retorna o dicionário da sua arma (acerto, rolags, dano, etc.)

    # 4) aplica bônus no ACERTO
    _add_bonus_ataque(res, bonus_ataque)

    # 5) aplica bônus no DANO e os dados extras (se houver)
    faces = arma_dano_faces.get(arma)
    extras = _rola_extras(faces, dados_extras) if (dados_extras and faces) else []
    res["Dano"] = int(res.get("Dano", 0)) + int(bonus_dano_flat) + sum(extras)
    _append_rolagens(res, extras)

    # 6) metadados úteis para debug/UI
    res["Arma"] = arma
    res["Postura"] = postura
    res["Estilo Oculto"] = estilo
    res["Bônus Estilo (ataque/dano)"] = bonus_estilo
    if postura == 'Postura do Sol':
        res["Bônus Postura (ataque)"] = 2
        res["Dados extras de dano"] = f"+1d{faces}" if faces else "+1 dado (definir faces)"

    return res

def cast_execucao_silenciosa():
    """Execução Silenciosa: rola ataque armado + dano extra 1d8 (+1d8 a cada 4 níveis)."""
    # 1) pega o ataque normal
    base_res = cast_ataque_armado()

    # 2) quantidade de d8 extras (mínimo 1)
    dados_extra = (nivel // 4) + 1
    extras = _rola_extras(8, dados_extra)

    # 3) aplica os dados extras no resultado
    base_res["Dano"] += sum(extras)
    _append_rolagens(base_res, extras)

    # 4) marca no log
    base_res["Habilidade"] = f"{base_res['Habilidade']} + Execução Silenciosa"
    base_res["Descrição Extra"] = f"Execução Silenciosa: +{dados_extra}d8 de dano."

    return base_res

def cast_corte_oculto():
    """
    Corte Oculto:
      - Base: cast_ataque_armado()
      - +1 dado da arma + FOR
      - Se for CRIT, o +1 dado entra no cálculo do crítico (vira +2 dados no resultado final).
        (crit atual x6 => regra efetiva já aplicada na função base; aqui apenas ajustamos os dados extras)
    """
    res = cast_ataque_armado()

    arma = res.get("Arma") or arma_atual
    faces = arma_dano_faces.get(arma)
    if not faces:
        # se não souber as faces, não dá pra rolar dado extra corretamente
        res["Descrição Extra"] = (res.get("Descrição Extra", "") + " | Corte Oculto: definir faces do dado da arma.").strip(" |")
        return res

    # detecta CRIT pelo texto (seu retorno tem "(CRIT)" na descrição)
    desc = (res.get("Descrição") or res.get("Descricao") or "").upper()
    is_crit = "CRIT" in desc

    # +1d<faces> (normal) ou +2d<faces> (se CRIT, pq entra dentro do cálculo do crítico)
    dados_extras = 2 if is_crit else 1
    extras = _rola_extras(faces, dados_extras)

    # bônus de FOR (flat, não multiplicado)
    for_bonus = 0
    try:
        for_bonus = mod(For)  # se você já tiver mod(For) no escopo
    except Exception:
        for_bonus = globals().get("mod_for", 0)

    # aplica no resultado
    res["Dano"] = int(res.get("Dano", 0)) + sum(extras) + int(for_bonus)
    _append_rolagens(res, extras)

    # marca metadados
    res["Habilidade"] = f"{res.get('Habilidade','Ataque')} + Corte Oculto"
    add_txt = f"Corte Oculto: +{dados_extras}d{faces} {'(crit)' if is_crit else ''} + FOR({for_bonus})."
    res["Descrição Extra"] = (res.get("Descrição Extra", "") + (" | " if res.get("Descrição Extra") else "") + add_txt)

    return res

def cast_corte_oculto_ritual():
    """
    Corte Oculto:
      - Base: cast_ataque_armado()
      - +3 dado da arma + FOR
      - Se for CRIT, o +3 dado entra no cálculo do crítico (vira +6 dados no resultado final).
        (crit atual x6 => regra efetiva já aplicada na função base; aqui apenas ajustamos os dados extras)
    """
    res = cast_ataque_armado()

    arma = res.get("Arma") or arma_atual
    faces = arma_dano_faces.get(arma)
    if not faces:
        # se não souber as faces, não dá pra rolar dado extra corretamente
        res["Descrição Extra"] = (res.get("Descrição Extra", "") + " | Corte Oculto: definir faces do dado da arma.").strip(" |")
        return res

    # detecta CRIT pelo texto (seu retorno tem "(CRIT)" na descrição)
    desc = (res.get("Descrição") or res.get("Descricao") or "").upper()
    is_crit = "CRIT" in desc

    # +1d<faces> (normal) ou +2d<faces> (se CRIT, pq entra dentro do cálculo do crítico)
    dados_extras = 6 if is_crit else 3
    extras = _rola_extras(faces, dados_extras)

    # bônus de FOR (flat, não multiplicado)
    for_bonus = 0
    try:
        for_bonus = mod(For)  # se você já tiver mod(For) no escopo
    except Exception:
        for_bonus = globals().get("mod_for", 0)

    # aplica no resultado
    res["Dano"] = int(res.get("Dano", 0)) + sum(extras) + int(for_bonus)
    _append_rolagens(res, extras)

    # marca metadados
    res["Habilidade"] = f"{res.get('Habilidade','Ataque')} + Corte Oculto"
    add_txt = f"Corte Oculto: +{dados_extras}d{faces} {'(crit)' if is_crit else ''} + FOR({for_bonus})."
    res["Descrição Extra"] = (res.get("Descrição Extra", "") + (" | " if res.get("Descrição Extra") else "") + add_txt)

    return res

def cast_convergencia():
	rols = dado(8, 3)
	return {
	"Habilidade": "Convergência, 血を流す",
    "Custo": 1,
	"Alcance": "12m",
	"CD do TR": cd_do_tr,
    "Descrição": "Converge legal",
	"Rolagens": rols,
	"Dano (3d8)": sum(rols)+mod(Int),
	}

def cast_sangue_perfurante():
	rols = dado(8, 8)
	acerto = dado(20)[0]+feiticaria
	crit_threshold = 20+feiticaria
	crit_rols = dado(8,16)
	if acerto >= crit_threshold:
		return {
		"Habilidade": "Sangue Perfurante",
        "Custo": 4,
		"Alcance": "18m",
        "Descrição": "Perfura com sangue mt potente",
		"Rolagem de Ataque": str(acerto)+"(CRIT)",
		"Rolagens": crit_rols,
		"Dano (16d8)": sum(crit_rols)+mod(Int),
		}
	else:
		return {
		"Habilidade": "Sangue Perfurante",
        "Custo": 4,
		"Alcance": "18m",
        "Descrição": "Perfura com sangue",
		"Rolagem de Ataque": acerto,
		"Rolagens": rols,
		"Dano (8d8)": sum(rols)+mod(Int),
		}
    
def cast_poca_de_sangue():
	rols = dado(8, 7)
	rodadas = dado(2)[0]+1
	return {
	"Habilidade": "Byakuren, Chi Damari",
    "Custo": 4,
	"Alcance": "18m",
	"CD do TR": cd_do_tr,
    "Descrição": "Cria uma poça de sangue que dura "+ str(rodadas)+" rodadas",
	"Rolagens": rols,
	"Dano (3d8)": sum(rols)+mod(Int),
	}

def cast_poca_de_sangue_permanencia():
	rols = dado(12, 4)
	return {
	"Habilidade": "Byakuren, Chi Damari",
	"Alcance": "Um quadrado (1,5m)",
	"CD do TR": cd_do_tr,
    "Descrição": "Com a poça de sangue ainda no chão, tu vai tomando",
	"Rolagens": rols,
	"Dano (4d12)": sum(rols)+mod(Int),
	}

def cast_turbilhao_de_sangue():
	rols = dado(8, 3)
	return {
	"Habilidade": "Turbilhão de Sangue",
	"Alcance": "6m, raio 3m",
	"CD do TR": cd_do_tr,
    "Descrição": "Liga o liquidificador",
	"Rolagens": rols,
	"Dano (7d8)": sum(rols)+mod(Int),
	}

def cast_sangramento():
	rols = dado(8, 2)
	return {
	"Habilidade": "Sangramento - Turbilhão",
	#"Alcance": "-",
	"CD do TR": cd_do_tr,
    "Descrição": "Sangra legal até passar no teste",
	"Rolagens": rols,
	"Dano (7d8)": sum(rols)+mod(Int),
	}


# Perícias - ETL

df = pd.read_csv('pericias.csv')



# Perícias com Maestria
per_com_maestria = ['Atletismo', 'Luta', 'Pontaria','Fortitude', 'Integridade','Percepção', 'Vontade','Astúcia', 'Feitiçaria', 'Ferreiro', 'Artesão']
per_com_especializacao = ['Fortitude', 'Feitiçaria', 'Ferreiro']
per_outrosmenos6 = -6
per_com_outrosmenos6 = ['Furtividade']
per_outrosmenos4 = -4
per_com_outrosmenos4 = ['Reflexos']
per_outrosmenos2 = -2
per_com_outrosmenos2 = ['Acrobacia', 'Prestidigitação']
per_outros2 = 2
per_com_outros2 = ['Fortitude', 'Feitiçaria', 'Pontaria']
per_outros4 = 4
per_com_outros4 = ['Atletismo', 'Luta']
per_outros6 = 6
per_com_outros6 = ['Artesão']
per_outros7 = 7
per_com_outros7 = ['Ferreiro']


# 1) mapa tolerante de rótulos de atributo -> modificador
attr_mod_map = {
    "for": mod(For), "força": mod(For), "forca": mod(For), "str": mod(For),
    "des": mod(Des), "dex": mod(Des), "destreza": mod(Des),
    "con": mod(Con), "constituição": mod(Con), "constituicao": mod(Con),
    "int": mod(Int), "inteligência": mod(Int), "inteligencia": mod(Int),
    "sab": mod(Sab), "sabedoria": mod(Sab),
    "car": mod(Car), "carisma": mod(Car),
}

# 2) normaliza nomes de colunas (com ou sem acento)
col_pericia = "Pericia" if "Pericia" in df.columns else "Pericia"

# 3) componentes
df["ModAtrib"] = df["Atributo"].map(lambda s: attr_mod_map.get(str(s).strip().lower(), 0))
df["LvlHalf"]  = nivel // 2
df["Maestria"] = np.where(df[col_pericia].isin(per_com_maestria), maestria, 0)
df['Especializacao'] = np.where(df[col_pericia].isin(per_com_especializacao), maestria//2, 0)
df["Outros2"]   = np.where(df[col_pericia].isin(per_com_outros2), per_outros2, 0)
df["Outros4"]   = np.where(df[col_pericia].isin(per_com_outros4), per_outros4, 0)
df["Outros6"]   = np.where(df[col_pericia].isin(per_com_outros6), per_outros6, 0)
df["Outros7"]   = np.where(df[col_pericia].isin(per_com_outros7), per_outros7, 0)
df["Outrosmenos6"]   = np.where(df[col_pericia].isin(per_com_outrosmenos6), per_outrosmenos6, 0)
df["Outrosmenos4"]   = np.where(df[col_pericia].isin(per_com_outrosmenos4), per_outrosmenos4, 0)
df["Outrosmenos2"]   = np.where(df[col_pericia].isin(per_com_outrosmenos2), per_outrosmenos2, 0)


# 4) total final
df["Total"] = df["ModAtrib"] + df["LvlHalf"] + df["Maestria"] + df['Especializacao'] + df["Outros2"] + df["Outros4"] + df["Outros6"] + df["Outros7"]+ df["Outrosmenos6"]+ df["Outrosmenos4"]+ df["Outrosmenos2"]


# Perícia da porrada
feiticaria = int(df.loc[df["Pericia"] == "Feitiçaria", "Total"].values[0])


# ---------------------------
# LAYOUT
# ---------------------------
#st.title("Ficha - Ryuzaki Kamo")

# ----- Colunas principais
col_ficha, col_pericias, col_habs = st.columns([2, 3, 2], gap="large")

st.sidebar.title('Shoji Yoshiro')
st.sidebar.image('shoji.png')
st.sidebar.subheader('Quem é O Homem?')
st.sidebar.write('Shoji é o cara que bate na cara de piranha, corta carros ao meio e os krl.')
st.sidebar.write('')
st.sidebar.write('O literal maior assassino do mundo Jujutsu.')


# ----- Col Pericias
with col_pericias:
    pericias_ui(df)


# ----- Coluna Habilidades


def escolher_postura(posturas: list) -> str:
     return st.selectbox(label='Assumir Postura', options=posturas, key='postura_selecionada')

def escolher_estilo_oculto(estilo_oculto: list) -> str:
     return st.selectbox(label='Estilo Oculto', options=estilo_oculto, key='estilo_oculto_selecionado')

def escolher_arma(armas: list) -> str:
     return st.selectbox(label='Armas', options=armas, key='arma_selecionada')

def toggle_golpe_descendente(default=False) -> bool:
    return st.checkbox(label='Golpe Descendente',
                       key='golpe_descendente_atual',
                       value=default)

def select_ca_outros(default: int = 0, min_value: int = -50, max_value: int = 50) -> int:
    # usa o último valor salvo como default nos reruns
    val = int(st.session_state.get('ca_outros_atual', default))
    return st.number_input(
        label='Modificadores de CA extra',
        value=val,
        step=1,
        min_value=min_value,
        max_value=max_value,
        key='ca_outros_atual',
        format="%d",
    )

with col_habs:
    st.subheader("Buffs/Armas")
    # Botoes e os krl
    b1, b2 = st.columns(2)
    with b1:
        estilo_oculto_atual = escolher_estilo_oculto(estilo_oculto)
    with b2:
        postura_atual = escolher_postura(posturas)
    b21, b22 = st.columns(2)
    with b21:
        arma_atual = escolher_arma(armas)
    with b22:
        ca_outros_atual = select_ca_outros(default=0)
    b31, b32 = st.columns(2)
    with b31:
        golpe_descendente_atual = toggle_golpe_descendente(default=False)
    
    st.subheader('Habilidades')

    # --- botões (apenas definem o 'clicked')
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
#    c5, c6 = st.columns(2)

    clicked = None
    if c1.button("Ataque Armado", use_container_width=True):
        clicked = ("Ataque Armado", cast_ataque_armado())
    if c2.button("Execução Silenciosa", use_container_width=True):
        clicked = ("Execução Silenciosa", cast_execucao_silenciosa())
    if c3.button("Corte Oculto", use_container_width=True):
        clicked = ("Corte Oculto", cast_corte_oculto())
    if c4.button("Corte Oculto - Ritual", use_container_width=True):
        clicked = ("Corte Oculto - Ritual (Ação completa)", cast_corte_oculto_ritual())
#    if c5.button("Placeholder 2", use_container_width=True):
#        clicked = ("Turbilhão de Sangue", cast_turbilhao_de_sangue())
#    if c6.button("Placeholder 3", use_container_width=True):
#        clicked = ("Turbilhão de Sangue - Sangramento", cast_sangramento())

    # salva o último output clicado
    if clicked:
        st.session_state["last_output"] = clicked

    # --- render fixo do output (sempre abaixo do '---')
    if "last_output" in st.session_state:
        title, payload = st.session_state["last_output"]
        show_result(title, payload)
    else:
        st.caption("Clique numa habilidade para rolar.")

    st.markdown("---")

    st.subheader("Perícias")
    # Resultado fixo acima da tabela
    if "skill_last_output" in st.session_state:
        title, payload = st.session_state["skill_last_output"]
        show_result(title, payload)
    else:
        st.caption("Clique no valor Total para rolar a perícia.")


#def modificadores_ca(modificador_ca) -> int:
def mod_ca_golpe_descendente() -> int:
    if golpe_descendente_atual is True:
        return maestria
    else:
        return 0
    
def mod_ca_postura() -> int:
    if postura_atual == 'Postura do Sol':
        return -4
    else:
        return 0
    
modificadores_ca = mod_ca_golpe_descendente() + mod_ca_postura() + ca_outros_atual

# ----- Coluna Ficha (sidebar visual)
with col_ficha:
    st.subheader("📜 Ficha do Personagem")
    with st.container(border=True):
        st.markdown("#### Nível e Recursos")
        c1, c2, c3 = st.columns(3)
        c1.metric("Nível", nivel)
        c2.metric(f"Maestria", maestria)
        c3.metric("CA Base/CA Atual", str(CA)+'/'+str(CA+modificadores_ca))
        c1.metric("PV", PV)
        c2.metric("PE", PE)
        c3.metric("PE Maximo (Armazenado)", PE_maximo_armazenado)

        # estado inicial (iguais ao máximo)
        if "pv_atual" not in st.session_state:
            st.session_state.pv_atual = PV
        if "pe_atual" not in st.session_state:
            st.session_state.pe_atual = PE
        if "pe_armazenado_atual" not in st.session_state:
            st.session_state.pe_armazenado_atual = PE_maximo_armazenado

        # uma única linha com inputs, alinhados com PV/PE
        c1.number_input("PV atual", min_value=-PV//2, step=1, key="pv_atual")
        c2.number_input("PE atual", min_value=0, max_value=PE, step=1, key="pe_atual")
        c3.number_input("PE Armazenado Atual", min_value=0, max_value=PE_maximo_armazenado, step=1, key="pe_armazenado_atual")


        st.markdown("---")
        st.markdown("#### Atributos")
        a1, a2 = st.columns(2)
        a1.write(f"**For**: {For} ({mod(For):+d})")
        a1.write(f"**Des**: {Des} ({mod(Des):+d})")
        a1.write(f"**Con**: {Con} ({mod(Con):+d})")
        a2.write(f"**Int**: {Int} ({mod(Int):+d})")
        a2.write(f"**Sab**: {Sab} ({mod(Sab):+d})")
        a2.write(f"**Car**: {Car} ({mod(Car):+d})")
        st.markdown("### 🧾 Histórico")
    
    if "history" in st.session_state and st.session_state.history:
        for item in st.session_state.history[:10]:
            with st.expander(f"[{item['ts']}] {item['msg']}", expanded=False):
                st.json(item["payload"], expanded=False)
    else:
        st.caption("Sem rolagens ainda. Lance uma habilidade!")

#st.sidebar.subheader('Debugging')
#st.sidebar.write('postura atual: '+str(postura_atual))
#st.sidebar.write('arma atual: '+str(arma_atual))
#st.sidebar.write('estilo oculto atual: '+str(estilo_oculto_atual))
#st.sidebar.write('Status golpe descendente atual abaixo')
#st.sidebar.write(golpe_descendente_atual)
#st.sidebar.write('CA atual abaixo')
#st.sidebar.write(CA+modificadores_ca)
