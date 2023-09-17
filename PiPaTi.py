import random
import json
from pathlib import Path
import unicodedata
import re
from enum import Enum


class Player(object):
    def __init__(self, name):
        self.name = name.capitalize()
        self.history = {
            "vde": [0, 0, 0],

            "mt_victorias":
                {'pipi': 1, 'pipa': 1, 'piti': 1, 'papi': 1, 'papa': 1, 'pati': 1, 'tipi': 1, 'tipa': 1, 'titi': 1},
            "mt_derrotas":
                {'pipi': 1, 'pipa': 1, 'piti': 1, 'papi': 1, 'papa': 1, 'pati': 1, 'tipi': 1, 'tipa': 1, 'titi': 1},
            "mt_empates":
                {'pipi': 1, 'pipa': 1, 'piti': 1, 'papi': 1, 'papa': 1, 'pati': 1, 'tipi': 1, 'tipa': 1, 'titi': 1},

            "pipati_prob": [1 / 3, 1 / 3, 1 / 3]
        }
        self.filename = Path.cwd().joinpath("json", "players", f"{self.name.lower()}.json")

    def load(self):
        try:
            with open(self.filename) as f:
                self.history = json.load(f)
        except FileNotFoundError:
            pass

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.history, f, indent=4)

    def total_partidas(self):
        return sum(self.history["vde"])

    def porcentaje_victorias(self):
        total = self.total_partidas()
        if total > 0:
            try:
                porcentaje = (self.history.get("vde")[0] / total)
                return porcentaje
            except NameError:
                return 0
        return 0


class Choice(int, Enum):
    PIEDRA = 1
    PAPEL = 2
    TIJERAS = 3


def pipati(jugador, verbose=False):
    historial = jugador.history
    continuar_jugando = True

    while continuar_jugando:
        option = 4
        jugador.save()
        while option > 3 or option < 0:
            try:
                option = int(input(
                    f"1: {Choice.PIEDRA.name.capitalize()}, "
                    f"2: {Choice.PAPEL.name.capitalize()}, "
                    f"3: {Choice.TIJERAS.name.capitalize()}  0: Salir\n"))
            except ValueError:
                print("Solo admite números enteros. \n")
            if option > 3 or option < 0:
                print("Inserte un número válido.\n")
        if option == 0:
            print(f"¡Gracias por jugar, {user.name.capitalize()}!\n")
            print("Has ganado %d veces." % historial["vde"][0])
            print("Has perdido %d veces." % historial["vde"][1])
            print("Has empatado %d veces." % historial["vde"][2])
            porcentaje = "{percent:.2%}".format(percent=jugador.porcentaje_victorias())
            print("Tu porcentaje de victorias es %s de un total de %d partidas.\n"
                  % (porcentaje, jugador.total_partidas()))
            continuar_jugando = False
            plv = construir_matriz_de_transicion("Ganado!", historial)
            pld = construir_matriz_de_transicion("!", historial)
            ple = construir_matriz_de_transicion("Empatado!", historial)
            if verbose:
                print("Tu matriz de transición de victorias es:\nPi: %s\nPa: %s\nTi: %s\n" % (plv[0], plv[1], plv[2]))
                print("Tu matriz de transición de derrotas es:\nPi: %s\nPa: %s\nTi: %s\n" % (pld[0], pld[1], pld[2]))
                print("Tu matriz de transición de empates es:\nPi: %s\nPa: %s\nTi: %s\n" % (ple[0], ple[1], ple[2]))
        else:
            try:
                matriz_de_transicion = construir_probabilidades_de_transicion(
                    eleccion_previa, option, resultado, historial)
                election_ia = random.randint(1, 100)
                historial["pipati_prob"][0] = matriz_de_transicion[eleccion_previa - 1][0]
                historial["pipati_prob"][1] = matriz_de_transicion[eleccion_previa - 1][1]
                historial["pipati_prob"][2] = matriz_de_transicion[eleccion_previa - 1][2]
                probabilidad_piedra = historial["pipati_prob"][0] * 100
                probabilidad_papel = historial["pipati_prob"][1] * 100 + probabilidad_piedra
                if election_ia <= probabilidad_piedra:
                    election_ia = 2
                elif election_ia <= probabilidad_papel:
                    election_ia = 3
                else:
                    election_ia = 1

                resultado = obtener_resultado(option, election_ia)

            except NameError:
                election_ia = random.randint(1, 3)
                resultado = obtener_resultado(option, election_ia)
            eleccion_previa = option
            print(f"{jugador.name}: %s" % Choice(option).name.capitalize())
            print("Máquina: %s" % Choice(election_ia).name.capitalize())
            print("¡Has %s" % resultado)
            if resultado == "Ganado!":
                historial["vde"][0] += 1
            elif resultado == "Perdido!":
                historial["vde"][1] += 1
            else:
                historial["vde"][2] += 1


def construir_probabilidades_de_transicion(ultima_eleccion, eleccion_actual, resultado_anterior, h):
    choi = ['pi', 'pa', 'ti']

    if resultado_anterior == "Ganado!":
        for i, x in h["mt_victorias"].items():
            if '%s%s' % (choi[ultima_eleccion - 1], choi[eleccion_actual - 1]) == i:
                h["mt_victorias"]['%s%s' % (choi[ultima_eleccion - 1], choi[eleccion_actual - 1])] += 1
    elif resultado_anterior == "Empatado!":
        for i, x in h["mt_empates"].items():
            if '%s%s' % (choi[ultima_eleccion - 1], choi[eleccion_actual - 1]) == i:
                h["mt_empates"]['%s%s' % (choi[ultima_eleccion - 1], choi[eleccion_actual - 1])] += 1
    else:
        for i, x in h["mt_derrotas"].items():
            if '%s%s' % (choi[ultima_eleccion - 1], choi[eleccion_actual - 1]) == i:
                h["mt_derrotas"]['%s%s' % (choi[ultima_eleccion - 1], choi[eleccion_actual - 1])] += 1

    return construir_matriz_de_transicion(resultado_anterior, h)


def construir_matriz_de_transicion(ra2, h2):
    n = 3
    m = 3
    t_m_v = [[0] * m for i in range(n)]
    t_m_d = [[0] * m for i in range(n)]
    t_m_e = [[0] * m for i in range(n)]

    if ra2 == "Ganado!":
        piedra = h2["mt_victorias"]['pipi'] + h2["mt_victorias"]['piti'] + h2["mt_victorias"]['pipa']
        papel = h2["mt_victorias"]['papi'] + h2["mt_victorias"]['pati'] + h2["mt_victorias"]['papa']
        tijeras = h2["mt_victorias"]['tipi'] + h2["mt_victorias"]['titi'] + h2["mt_victorias"]['tipa']
        choi = ['pi', 'pa', 'ti']
        for row_index, row in enumerate(t_m_v):
            for col_index, item in enumerate(row):
                a = int(h2["mt_victorias"]['%s%s' % (choi[row_index], choi[col_index])])
                if row_index == 0:
                    c = a / piedra
                elif row_index == 1:
                    c = a / papel
                else:
                    c = a / tijeras
                row[col_index] = float(c)
        return t_m_v
    elif ra2 == "Empatado!":
        piedra = h2["mt_empates"]['pipi'] + h2["mt_empates"]['piti'] + h2["mt_empates"]['pipa']
        papel = h2["mt_empates"]['papi'] + h2["mt_empates"]['pati'] + h2["mt_empates"]['papa']
        tijeras = h2["mt_empates"]['tipi'] + h2["mt_empates"]['titi'] + h2["mt_empates"]['tipa']
        choi = ['pi', 'pa', 'ti']
        for row_index, row in enumerate(t_m_e):
            for col_index, item in enumerate(row):
                a = int(h2["mt_empates"]['%s%s' % (choi[row_index], choi[col_index])])
                if row_index == 0:
                    c = a / piedra
                elif row_index == 1:
                    c = a / papel
                else:
                    c = a / tijeras
                row[col_index] = float(c)
        return t_m_e

    else:
        piedra = h2["mt_derrotas"]['pipi'] + h2["mt_derrotas"]['piti'] + h2["mt_derrotas"]['pipa']
        papel = h2["mt_derrotas"]['papi'] + h2["mt_derrotas"]['pati'] + h2["mt_derrotas"]['papa']
        tijeras = h2["mt_derrotas"]['tipi'] + h2["mt_derrotas"]['titi'] + h2["mt_derrotas"]['tipa']
        choi = ['pi', 'pa', 'ti']
        for row_index, row in enumerate(t_m_d):
            for col_index, item in enumerate(row):
                a = int(h2["mt_derrotas"]['%s%s' % (choi[row_index], choi[col_index])])
                if row_index == 0:
                    c = a / piedra
                elif row_index == 1:
                    c = a / papel
                else:
                    c = a / tijeras
                row[col_index] = float(c)
        return t_m_d


def obtener_resultado(player, machine):
    if player == 1:
        if machine == 3:
            return "Ganado!"
        elif machine == 2:
            return "Perdido!"
        elif machine == 1:
            return "Empatado!"
        else:
            print("Por extrañas circunstancias la máquina eligió: %s" % machine)
    elif player == 2:
        if machine == 3:
            return "Perdido!"
        elif machine == 2:
            return "Empatado!"
        elif machine == 1:
            return "Ganado!"
        else:
            print("Por extrañas circunstancias la máquina eligió: %s" % machine)
    else:
        if machine == 3:
            return "Empatado!"
        elif machine == 2:
            return "Ganado!"
        elif machine == 1:
            return "Perdido!"
        else:
            print("Por extrañas circunstancias la máquina eligió: %s" % machine)
    return "Ganado!"


def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


if __name__ == '__main__':
    path = Path.cwd().joinpath("json", "players")
    existe = path.exists()
    if not existe:
        Path.mkdir(path)
    username = slugify(input("Inserte su nombre:\n")).lower()
    if not username:
        username = "anonymous"
    user = Player(username)
    user.load()
    if user.history.get('vde') != [0, 0, 0]:
        porc = user.porcentaje_victorias()
        if porc < 0.1:
            msg = ". Deberías dedicarte a otra cosa, está claro que eres malísimo jugando a esto."
        elif 0.1 <= porc < 0.2:
            msg = ". Si quieres seguir perdiendo... allá tu."
        else:
            msg = ". Te deseo suerte."
        print("Hola de nuevo,", user.name+msg)
        pipati(user)
    else:
        user.save()
        print(f"¡Bienvenido a PaPeTi.py, {user.name}!.\n"
              f"Vas a ser humillado sin miramientos jugando a Piedra Papel Tijeras.\n")
        pipati(user)
