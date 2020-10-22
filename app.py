

from flask import Flask, Response

from flask import request

import random
import sys
import os
app = Flask(__name__)
size = 8
@app.route('/')
def hello_world():
    turno = request.args.get('turno')
    
    estado = request.args.get('estado')

    result = iniciar(turno,estado)
    
    return result

def obtenerTablero(estado):
    tablero = []
    for i in range(size):
        tablero.append([' '] * size)
    cont = 0
    for i in range(8):
        for j in range(8):
            if estado[cont] =='2':
                tablero[i][j] = ' '
            else :
                tablero[i][j] = estado[cont]
            
            cont += 1

    return tablero

def estaEnTablero(x, y):
    # Devuelve True si las coordenadas se encuentran dentro del tablero
    return x >= 0 and x < size and y >= 0 and y < size

def esJugadaValida(tablero, baldosa, comienzox, comienzoy):
    # Devuelve False si la jugada del jugador en comienzox, comienzoy es invalida.
    # Si es una jugada válida, devuelve una lista de espacios que pasarían a ser del jugador si moviera aquí.
    if tablero[comienzox][comienzoy] != ' ' or not estaEnTablero(comienzox, comienzoy):
        return False

    tablero[comienzox][comienzoy] = baldosa # coloca temporariamente la baldosa sobre el tablero.

    if baldosa == '1':
        otraBaldosa = '0'
    else:
        otraBaldosa = '1'

    baldosasAConvertir = []
    for direcciónx, direccióny in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = comienzox, comienzoy
        x += direcciónx # primer paso en la dirección
        y += direccióny # primer paso en la dirección
        if estaEnTablero(x, y) and tablero[x][y] == otraBaldosa:
            # Hay una pieza perteneciente al otro jugador al lado de nustra pieza
            x += direcciónx
            y += direccióny
            if not estaEnTablero(x, y):
                continue
            while tablero[x][y] == otraBaldosa:
                x += direcciónx
                y += direccióny
                if not estaEnTablero(x, y): # sale del bucle while y continua en el bucle for.
                    break
            if not estaEnTablero(x, y):
                continue
            if tablero[x][y] == baldosa:
                # Hay fichas a convertir. Caminar en dirección opuesta hasta llegar al casillero original, registrando todas las posiciones en el camino.
                while True:
                    x -= direcciónx
                    y -= direccióny
                    if x == comienzox and y == comienzoy:
                        break
                    baldosasAConvertir.append([x, y])

    tablero[comienzox][comienzoy] = ' ' # restablecer el espacio vacío
    if len(baldosasAConvertir) == 0: # Si no se convirtió ninguna baldosa, la jugada no es válida.
        return False
    return baldosasAConvertir

def obtenerJugadasValidas(tablero, baldosa):
    # Devuelve una lista de listas [x,y] de jugadas válidas para el jugador en el tablero dado.
    jugadasValidas = []

    for x in range(size):
        for y in range(size):
            if esJugadaValida(tablero, baldosa, x, y) != False:
                jugadasValidas.append([x, y])
    return jugadasValidas

def esEsquina(x, y):
    # Devuelve True si la posicion es una de las esquinas.
    return (x == 0 and y == 0) or (x == 7 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 7)

def obtenerNuevoTablero():
    # Crea un tablero nuevo, vacío.
    tablero = []
    for i in range(size):
        tablero.append([' '] * size)

    return tablero


def obtenerCopiaTablero(tablero):
    # Duplica la lista del tablero y devuelve el duplicado.
    replicaTablero = obtenerNuevoTablero()

    for x in range(size):
        for y in range(size):
            replicaTablero[x][y] = tablero[x][y]

    return replicaTablero

def hacerJugada(tablero, baldosa, comienzox, comienzoy):
    # Coloca la baldosa sobre el tablero en comienzox, comienzoy, y convierte cualquier baldosa del oponente.
    # Devuelve False si la jugada es inválida, True si es válida.
    baldosasAConvertir = esJugadaValida(tablero, baldosa, comienzox, comienzoy)

    if baldosasAConvertir == False:
        return False

    tablero[comienzox][comienzoy] = baldosa
    for x, y in baldosasAConvertir:
        tablero[x][y] = baldosa
    return True

def obtenerPuntajeTablero(tablero):
    # Determina el puntaje contando las piezas. Devuelve un diccionario con claves 'X' y 'O'.
    puntajex = 0
    puntajeo = 0
    for x in range(size):
        for y in range(size):
            if tablero[x][y] == '1':
                puntajex += 1
            if tablero[x][y] == '0':
                puntajeo += 1
    return {'1':puntajex, '0':puntajeo}

def obtenerJugadaComputadora(tablero, baldosaComputadora):
    # Dado un tablero y la baldosa de la computadora, determinar dónde
    # jugar y devolver esa jugada como una lista [x, y].
    jugadasPosibles = obtenerJugadasValidas(tablero, baldosaComputadora)

    # ordena al azar el orden de las jugadas posibles
    random.shuffle(jugadasPosibles)

    # siempre jugar en una esquina si está disponible.
    for x, y in jugadasPosibles:
        if esEsquina(x, y):
            return [x, y]

    # Recorrer la lista de jugadas posibles y recordar la que da el mejor puntaje
    mejorPuntaje = -1
    for x, y in jugadasPosibles:
        replicaTablero = obtenerCopiaTablero(tablero)
        hacerJugada(replicaTablero, baldosaComputadora, x, y)
        puntaje = obtenerPuntajeTablero(replicaTablero)[baldosaComputadora]
        if puntaje > mejorPuntaje:
            mejorJugada = [x, y]
            mejorPuntaje = puntaje
    return mejorJugada

def iniciar(turno, estado):
    tableroPrincipal = obtenerTablero(estado)
    if turno == '1':
        print('es uno')
        otraBaldosa = '0'
        x, y = obtenerJugadaComputadora(tableroPrincipal,'1')
    else:
        otraBaldosa = '1'
        x, y = obtenerJugadaComputadora(tableroPrincipal,'0')
    return str(x) + str(y)