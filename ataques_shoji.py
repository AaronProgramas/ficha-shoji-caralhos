import random
import math
from datetime import datetime
from html import escape
import pandas as pd
import numpy as np

def rolar_pericia(nome: str, total: int) -> dict:
    """Rola 1d20 + total para teste de perícia."""
    d20 = random.randint(1, 20)
    return {
        "Habilidade": f"Perícia – {nome}",
        "Rolagens": [d20],            # mostra o d20
        "Ataque": d20 + int(total),   # 'show_result' exibe como Ataque/Teste
    }

def dado(faces: int, vezes: int = 1) -> list[int]:
    """Rola 'vezes' dados de 'faces' e retorna a lista com os resultados."""
    return [random.randint(1, faces) for _ in range(vezes)]

def dado_cura_aprimorada(faces: int, vezes: int = 1) -> list[int]:
    return [random.randint(3, faces) for _ in range(vezes)]

def mod(atr: int) -> int:
    """Modificador de atributo: floor((atributo-10)/2)."""
    return (atr - 10) // 2

class ataque_armado:

    def espada_gancho():
        rols = dado(8, 1)
        acerto = dado(20)[0]+18
        crit_threshold = 19+18 # 19 no dado, 18 somado, tem q bater a meta pra critar
        crit_rols = dado(8,6)
        if acerto >= crit_threshold:
            return {
            "Habilidade": "Espada Gancho",
            "Alcance": "Pessoal",
            "Descrição": "Toma gancho de BANDIDO, piranha (CRIT)",
            "Rolagem de Ataque": acerto,
            "Rolagens": crit_rols,
            "Dano": sum(crit_rols)+12,
            }
        else:
            return {
            "Habilidade": "Espada Gancho",
            "Alcance": "Pessoal",
            "Descrição": "Toma gancho, piranha",
            "Rolagem de Ataque": acerto,
            "Rolagens": rols,
            "Dano": sum(rols)+12,
            }
        
    def espada_dupla():
        rols = dado(6, 3)
        acerto = dado(20)[0]+19
        crit_threshold = 19+19 # 19 no dado, 18 somado, tem q bater a meta pra critar
        crit_rols = dado(6,10)
        if acerto >= crit_threshold:
            return {
            "Habilidade": "Espada Dupla",
            "Alcance": "Pessoal",
            "Descrição": "Quer duas? Então vai tomando FIRME (CRIT)",
            "Rolagem de Ataque": acerto,
            "Rolagens": crit_rols,
            "Dano": sum(crit_rols)+12,
            }
        else:
            return {
            "Habilidade": "Espada Gancho",
            "Alcance": "Pessoal",
            "Descrição": "Quer duas? Então vai tomando.",
            "Rolagem de Ataque": acerto,
            "Rolagens": rols,
            "Dano": sum(rols)+12,
            }
        
    def espada_colossal():
        rols = dado(8, 3)
        acerto = dado(20)[0]+18
        crit_threshold = 20+18 # 19 no dado, 18 somado, tem q bater a meta pra critar
        crit_rols = dado(8,10)
        if acerto >= crit_threshold:
            return {
            "Habilidade": "Espada Colossal",
            "Alcance": "Pessoal",
            "Descrição": "Quer o meu colosso? (CRIT)",
            "Rolagem de Ataque": acerto,
            "Rolagens": crit_rols,
            "Dano": sum(crit_rols)+12,
            }
        else:
            return {
            "Habilidade": "Espada Colossal",
            "Alcance": "Pessoal",
            "Descrição": "Quer ver o meu colossal?",
            "Rolagem de Ataque": acerto,
            "Rolagens": rols,
            "Dano": sum(rols)+12,
            }
        
    def nunchako_pesado():
        rols = dado(8, 3)
        acerto = dado(20)[0]+16
        crit_threshold = 19+16 # 20 no dado, 16 somado, tem q bater a meta pra critar
        crit_rols = dado(8,10)
        if acerto >= crit_threshold:
            return {
            "Habilidade": "Nunchaco Pesado",
            "Alcance": "Pessoal",
            "Descrição": "Cacetete PMERJ, perfeito pra agredir civis (CRIT)",
            "Rolagem de Ataque": acerto,
            "Rolagens": crit_rols,
            "Dano": sum(crit_rols)+12,
            }
        else:
            return {
            "Habilidade": "Nunchako Pesado",
            "Alcance": "Pessoal",
            "Descrição": "Porrete estilo oriental",
            "Rolagem de Ataque": acerto,
            "Rolagens": rols,
            "Dano": sum(rols)+12,
            }
        
    def lanca_grande():
        rols = dado(8, 3)
        acerto = dado(20)[0]+16
        crit_threshold = 20+16 # 20 no dado, 16 somado, tem q bater a meta pra critar
        crit_rols = dado(8,10)
        if acerto >= crit_threshold:
            return {
            "Habilidade": "Lança Grande",
            "Alcance": "Pessoal",
            "Descrição": "Cacetete PMERJ, perfeito pra agredir civis (CRIT)",
            "Rolagem de Ataque": acerto,
            "Rolagens": crit_rols,
            "Dano": sum(crit_rols)+12,
            }
        else:
            return {
            "Habilidade": "Lança Grande",
            "Alcance": "Pessoal",
            "Descrição": "Porrete estilo oriental",
            "Rolagem de Ataque": acerto,
            "Rolagens": rols,
            "Dano": sum(rols)+12,
            }
        
    def machado_grande():
        rols = dado(6, 3)
        acerto = dado(20)[0]+16
        crit_threshold = 20+16 # 20 no dado, 16 somado, tem q bater a meta pra critar
        crit_rols = dado(8,10)
        if acerto >= crit_threshold:
            return {
            "Habilidade": "Machado Grande",
            "Alcance": "Pessoal",
            "Descrição": "Machadada potente no teu roxo (CRIT)",
            "Rolagem de Ataque": acerto,
            "Rolagens": crit_rols,
            "Dano": sum(crit_rols)+12,
            }
        else:
            return {
            "Habilidade": "Machado Grande",
            "Alcance": "Pessoal",
            "Descrição": "Toma machado",
            "Rolagem de Ataque": acerto,
            "Rolagens": rols,
            "Dano": sum(rols)+12,
            }
        
    def foice_grande():
        rols = dado(10, 3)
        acerto = dado(20)[0]+16
        crit_threshold = 20+16 # 20 no dado, 16 somado, tem q bater a meta pra critar
        crit_rols = dado(10,10)
        if acerto >= crit_threshold:
            return {
            "Habilidade": "Foice Grande",
            "Alcance": "Pessoal",
            "Descrição": "Foice potente no teu roxo (CRIT)",
            "Rolagem de Ataque": acerto,
            "Rolagens": crit_rols,
            "Dano": sum(crit_rols)+12,
            }
        else:
            return {
            "Habilidade": "Foice Grande",
            "Alcance": "Pessoal",
            "Descrição": "Toma foice",
            "Rolagem de Ataque": acerto,
            "Rolagens": rols,
            "Dano": sum(rols)+12,
            }
        
    def soqueira():
        rols = dado(6, 3)
        acerto = dado(20)[0]+16
        crit_threshold = 20+16 # 20 no dado, 16 somado, tem q bater a meta pra critar
        crit_rols = dado(8,10)
        if acerto >= crit_threshold:
            return {
            "Habilidade": "Soqueira",
            "Alcance": "Pessoal",
            "Descrição": "Socada potente no teu roxo (CRIT)",
            "Rolagem de Ataque": acerto,
            "Rolagens": crit_rols,
            "Dano": sum(crit_rols)+12,
            }
        else:
            return {
            "Habilidade": "Machado Grande",
            "Alcance": "Pessoal",
            "Descrição": "Toma soco",
            "Rolagem de Ataque": acerto,
            "Rolagens": rols,
            "Dano": sum(rols)+12,
            }
        
    def cardume_de_adagas():
        rols = dado(4, 1)
        acerto = dado(20)[0]+16
        crit_threshold = 19+16 # 20 no dado, 16 somado, tem q bater a meta pra critar
        crit_rols = dado(4,6)
        if acerto >= crit_threshold:
            return {
            "Habilidade": "Cardume de Adagas",
            "Alcance": "Pessoal",
            "Descrição": "Cardume potente entrando firme no teu roxo (CRIT)",
            "Rolagem de Ataque": acerto,
            "Rolagens": crit_rols,
            "Dano": sum(crit_rols)+12,
            }
        else:
            return {
            "Habilidade": "Cardume de Adagas",
            "Alcance": "Pessoal",
            "Descrição": "Toma uma porrada de adagas",
            "Rolagem de Ataque": acerto,
            "Rolagens": rols,
            "Dano": sum(rols)+12,
            }
        
    def adaga_de_aparar():
        rols = dado(4, 1)
        acerto = dado(20)[0]+16
        crit_threshold = 19+16 # 20 no dado, 16 somado, tem q bater a meta pra critar
        crit_rols = dado(4,6)
        if acerto >= crit_threshold:
            return {
            "Habilidade": "Adaga de Aparar",
            "Alcance": "Pessoal",
            "Descrição": "Cardume potente entrando firme no teu roxo (CRIT)",
            "Rolagem de Ataque": acerto,
            "Rolagens": crit_rols,
            "Dano": sum(crit_rols)+12,
            }
        else:
            return {
            "Habilidade": "Adaga de Aparar",
            "Alcance": "Pessoal",
            "Descrição": "Toma uma porrada de adagas",
            "Rolagem de Ataque": acerto,
            "Rolagens": rols,
            "Dano": sum(rols)+12,
            }
