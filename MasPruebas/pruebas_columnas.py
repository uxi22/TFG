import datetime
import sys
import os
from collections import defaultdict

import pandas as pd
from PIL import Image
from PySide6 import QtGui
from PySide6.QtCore import Qt, QRegularExpression, QRect, QSize, QPoint
from PySide6.QtGui import QScreen, QRegularExpressionValidator, QImage, QPolygon, QBrush, QColor, QPainter, QPen, \
    QFontMetricsF
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget, QHBoxLayout, QSpacerItem, QLineEdit, QPushButton, QPointList, QFrame
)

# Obtenemos la ruta al directorio del script
basedir = os.path.dirname(__file__)
basedir = os.path.join(basedir, os.pardir)

try:
    from ctypes import windll

    myappid = 'mycompany.myproduct.subproduct.version'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

arriba1 = [[1, 5], [5, 6], [4, 8], [9, 8], [9, 8], [7, 7], [6, 8], [10, 6]]  # del 18 al 11
arriba2 = [[7, 11], [6, 6], [7, 8], [8, 9], [8, 10], [7, 5], [5, 5], [2, 1]]  # del 21 al 28

dientes = [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28]

altura_rojo = [[0, 0, 0] for _ in range(16)]
altura_azul = [[0, 0, 0] for _ in range(16)]

style = "margin: 0.5px; border: 1px solid grey; border-radius: 3px;"
colorBoton = "background-color: #BEBEBE;"


def cambiar_color(boton, color):
    if boton:
        boton.setStyleSheet(style + f"background-color: {color}")
    else:
        boton.setStyleSheet(style + colorBoton)


def es_numero(texto):
    if len(texto) == 0:
        return False
    if texto[0] in ('-', '+'):
        return texto[1:].isdigit()
    return texto.isdigit()


def calcular_cal(i):
    print((sum(window.datos.profundidades[i]) / 3))
    print(sum(window.datos.margenes[i]) / 3)
    print((sum(window.datos.profundidades[i]) / 3 + sum(window.datos.margenes[i]) / 3) - 2)
    return (sum(window.datos.profundidades[i]) / 3 + sum(window.datos.margenes[i]) / 3) - 2


def aplanar_lista(lista):
    salida = []
    for i in lista:
        if isinstance(i, list):
            salida.extend(i)
        else:
            salida.append(i)
    return salida


def aplanar_abs_lista(lista):
    salida = []
    for i in lista:
        if isinstance(i, list):
            salida.extend(aplanar_abs_lista(i))
        else:
            salida.append(abs(i))
    return salida


class Input03(QLineEdit):
    def __init__(self, height, furca=False, numDiente=0, parent=None):
        super().__init__(parent)

        regex = QRegularExpression("[0-3]")
        self.setValidator(QRegularExpressionValidator(regex))
        self.setAlignment(Qt.AlignCenter)
        self.setPlaceholderText("0")
        self.editingFinished.connect(lambda: self.guardartexto(numDiente, furca))
        self.setStyleSheet("QLineEdit { " + style + "font-size: 10px; } QLineEdit:focus { border: 1px solid #C3C3C3; }")
        self.setGeometry(QRect(0, height, 45, 20))

    def guardartexto(self, numDiente, furca):
        if furca:
            # actualizar datos
            window.datos.actualizar_defecto_furca(numDiente, self.text())
            # Actualizar dibujo dientes
            window.widgetDientes.update()
        else:
            # actualizar datos
            window.datos.actualizar_movilidad(numDiente, self.text())


class InputSiNo3(QHBoxLayout):
    def __init__(self, numDiente, tipo, parent, height):
        super().__init__(parent)
        self.setGeometry(QRect(0, height, 45, 20))
        self.botones = []
        for n in range(1, 4):
            boton = QPushButton("")
            boton.setCheckable(True)
            boton.setStyleSheet("QPushButton { " + style + colorBoton + "}" +
                                "QPushButton:hover { background-color: #AAAAAA; }")
            boton.setDefault(True)
            boton.clicked.connect(lambda *args, ind=n-1, t=tipo: self.pulsar_boton(ind, numDiente, t))
            self.addWidget(boton)
            self.botones.append(boton)

    def pulsar_boton(self, ind, numDiente, tipo):
        boton = self.botones[ind]

        if tipo == 1:
            cambiar_color(boton, "#FF2B32")
            window.sangrado.actualizarPorcentajes(numDiente * 3 + ind, boton.isChecked())
            window.datos.actualizar_sangrado(int(numDiente), ind, boton.isChecked())
        elif tipo == 2:
            cambiar_color(boton, "#5860FF")
            window.placa.actualizarPorcentajes(int(numDiente) * 3 + ind, boton.isChecked())
            window.datos.actualizar_placa(int(numDiente), ind, boton.isChecked())
        elif tipo == 3:
            cambiar_color(boton, "#7CEBA0")
            # window.supuracion.actualizarPorcentajes(int(numDiente) * 3 + ind, boton.isChecked())
            window.datos.actualizar_supuracion(int(numDiente), ind, boton.isChecked())


class Input3(QHBoxLayout):
    def __init__(self, ndiente, tipo, height, parent):
        super().__init__(parent)
        self.setGeometry(QRect(0, height, 45, 20))
        self.validator = QRegularExpressionValidator(QRegularExpression(r"^[+-]?\d{1,2}$"))

        self.inpts = []
        for i in range(1, 4):
            inpt = QLineEdit()
            inpt.setValidator(self.validator)
            inpt.setStyleSheet("QLineEdit { " + style + "font-size: 10px; } QLineEdit:focus { border: 1px solid #C3C3C3; }")
            inpt.setPlaceholderText("0")
            inpt.editingFinished.connect(lambda ind=i-1: self.guardar_texto(ndiente, tipo, ind))
            self.addWidget(inpt)
            self.inpts.append(inpt)

    def guardar_texto(self, ndiente, tipo, num):
        inpt = self.inpts[num]
        if tipo == 1 and es_numero(inpt.text()):
            if -21 < int(inpt.text()) < 21:
                altura_rojo[int(ndiente)][num] = int(inpt.text())
                window.widgetDientes.actualizar_alturas(int(ndiente), tipo, num)
                window.widgetDientes.update()
                window.datos.actualizar_margen(int(ndiente), num, abs(int(inpt.text())))
                window.cal.actualizarDatos(int(ndiente), calcular_cal(int(ndiente)))
            else:
                inpt.setText("0")
        elif tipo == 2 and es_numero(inpt.text()):  # Profundidad de sondaje
            if 0 < int(inpt.text()) < 21:
                if (int(inpt.text()) >= 4):
                    self.inpts[num].setStyleSheet("QLineEdit { " + style + "color: crimson; font-size: 12px; }")
                else:
                    self.inpts[num].setStyleSheet("QLineEdit { " + style + "color: black; font-size: 12px; }")
                altura_azul[int(ndiente)][num] = int(inpt.text())
                window.widgetDientes.actualizar_alturas(int(ndiente), tipo, num)
                window.widgetDientes.update()
                window.ppd.actualizarDatos(int(ndiente) * 3 + num, abs(int(inpt.text())))
                window.cal.actualizarDatos(int(ndiente), calcular_cal(int(ndiente)))
                window.datos.actualizar_profundidad(int(ndiente), num, abs(int(inpt.text())))
            else:
                inpt.setText("0")




class Columna(QFrame):
    def __init__(self, numDiente, defFurca, left, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setGeometry(QRect(left, 0, 45, 180))

        self.incrementoHeight = 0

        botonNumeroDiente = QPushButton(str(dientes[numDiente]), self)
        botonNumeroDiente.setCheckable(True)
        botonNumeroDiente.setDefault(True)
        botonNumeroDiente.setStyleSheet(style + colorBoton + "font-weight: bold; font-size: 12px;")
        botonNumeroDiente.clicked.connect(lambda: self.desactivar_diente(numDiente, defFurca))
        botonNumeroDiente.setParent(self)
        botonNumeroDiente.setGeometry(QRect(0, self.incrementoHeight, 45, 20))
        self.incrementoHeight += 20

        self.hijos = [botonNumeroDiente]

        self.anhadir_elementos(numDiente, defFurca)

    def anhadir_elementos(self, numDiente, defFurca):
        # MOVILIDAD
        movilidad = Input03(self.incrementoHeight, False, numDiente, self.parent)
        self.incrementoHeight += 20
        self.hijos.append(movilidad)

        # DEFECTO DE FURCA
        if defFurca:
            furca = Input03(self.incrementoHeight, True, numDiente, self.parent)
        else:
            furca = QLabel("", self)
            furca.setGeometry(QRect(0, self.incrementoHeight, 45, 20))
        self.incrementoHeight += 20
        self.hijos.append(furca)

        # IMPLANTE
        boton = QPushButton("", self)
        boton.setCheckable(True)
        boton.setStyleSheet("QPushButton { " + style + colorBoton + "} QPushButton:hover { background-color: #AAAAAA; }")
        boton.setDefault(True)
        boton.clicked.connect(lambda: self.diente_implante(numDiente, defFurca))
        boton.setGeometry(QRect(0, self.incrementoHeight, 45, 20))
        self.incrementoHeight += 20
        self.hijos.append(boton)

        # SANGRADO AL SONDAJE
        sangrado = InputSiNo3(numDiente, 1, self, self.incrementoHeight)
        self.incrementoHeight += 20
        self.hijos.append(sangrado)

        # PLACA
        placa = InputSiNo3(numDiente, 2, self, self.incrementoHeight)
        self.incrementoHeight += 20
        self.hijos.append(placa)

        # SUPURACIÓN
        supuracion = InputSiNo3(numDiente, 3, self, self.incrementoHeight)
        self.incrementoHeight += 20
        self.hijos.append(supuracion)

        # MARGEN GINGIVAL
        margenGingival = Input3(numDiente, 1, self.incrementoHeight, self)
        self.incrementoHeight += 20
        self.hijos.append(margenGingival)

        # PROFUNDIDAD DE SONDAJE
        profSondaje = Input3(numDiente, 2, self.incrementoHeight, self)
        self.incrementoHeight += 20
        self.hijos.append(profSondaje)

        if window and numDiente in window.datos.inicializados:
            movilidad.setText(str(window.datos.movilidad[numDiente]))
            if window.datos.implantes[numDiente]:
                boton.setChecked(True)
                cambiar_color(boton, "#333333")
            furca.setText(str(window.datos.defectosfurca[numDiente]))
            for i in range(0, 3):
                if window.datos.sangrados[numDiente + i]:
                    sangrado.layout().itemAt(i).widget().setChecked(True)
                    cambiar_color(sangrado.layout().itemAt(i).widget(), "#FF2B32")
                if window.datos.placas[numDiente + i]:
                    placa.layout().itemAt(i).widget().setChecked(True)
                    cambiar_color(placa.layout().itemAt(i).widget(), "#5860FF")
                if window.datos.supuraciones[numDiente + i]:
                    supuracion.layout().itemAt(i).widget().setChecked(True)
                    cambiar_color(supuracion.layout().itemAt(i).widget(), "#7CEBA0")
                margenGingival.layout().itemAt(i).widget().setText(str(window.datos.margenes[numDiente + i]))
                profSondaje.layout().itemAt(i).widget().setText(str(window.datos.profundidades[numDiente + i]))

    def diente_implante(self, numDiente, deffurca):
        boton = self.hijos[2]
        cambiar_color(boton, "#333333")
        # Actualizamos los datos
        window.datos.actualizar_implante(numDiente, boton.isChecked())
        # Actualizamos la imagen
        window.widgetDientes.actualizar_imagen()
        # Desactivamos el input de la furca si corresponde
        if deffurca == 1:
            inptfurca = self.hijos[3]
            inptfurca.deleteLater()
            if boton.isChecked():
                new = QLabel("")
                new.setParent(self)
                new.setGeometry(QRect(0, 60, 45, 20))
            else:
                if deffurca == 1:
                    new = Input03(60, True, numDiente, self.parent)
                else:
                    new = QLabel("")
                    new.setParent(self)
                    new.setGeometry(QRect(0, 60, 45, 20))
            self.hijos[3] = new

    def eliminar_elementos(self):
        while len(self.children()) > 1:
            hijo = self.hijos.pop()
            if isinstance(hijo, QHBoxLayout):
                self.vaciar_layout(hijo)
            else:
                hijo.deleteLater()

    def vaciar_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.vaciar_layout(child.layout())
        del layout

    def desactivar_diente(self, numDiente, defFurca):
        window.datos.actualizar_desactivados(int(numDiente))
        window.widgetDientes.update()

        if self.hijos[0].isChecked():
            self.eliminar_elementos()
            label = QLabel("", self)
            self.setGeometry(QRect(0, 20, 45, 160))
            self.hijos.append(label)
        else:
            while len(self.children()) > 1:
                hijo = self.hijos.pop()
                if isinstance(hijo, QWidget):
                    hijo.deleteLater()
            self.anhadir_elementos(numDiente, defFurca)


class CuadroColores(QWidget):
    def __init__(self, profundidades, margenes, n, parent=None):
        super().__init__(parent)
        self.setGeometry(QRect(0, 0, 265, 81))

        self.n = n
        if margenes != None:
            self.margenes = margenes
            self.profundidades = profundidades
            self.listadatos = [0] * 16
        else :
            self.listadatos = aplanar_lista(profundidades)

        self.datos = defaultdict(int)
        for i in self.listadatos:
            self.datos[int(i)] += 1

    def minimumSizeHint(self):
        return QSize(1, 1)

    def actualizarDatos(self, indice, nuevo):
        self.datos[self.listadatos[indice]] -= 1
        self.datos[nuevo] += 1
        self.listadatos[indice] = nuevo
        self.update()

    def paintEvent(self, event):
        self.setMinimumSize(265, 81)

        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing, True)

        if self.n == 4:
            text = "CAL"
            d = ["0", "1-2", "3-4", "≥5"]
            nsites = [str(self.datos[0]), str(self.datos[1] + self.datos[2]),
                      str(self.datos[3] + self.datos[4]),
                      str(sum(self.datos.values()) - sum([self.datos[i] for i in range(0, 5)]))]
        else:
            text = "PPD"
            d = ["0-3", "4", "5", "6-8", "≥9"]
            nsites = [str(self.datos[0] + self.datos[1] + self.datos[2] + self.datos[3]), str(self.datos[4]),
                      str(self.datos[5]), str(self.datos[6] + self.datos[7] + self.datos[8]),
                      str(sum(self.datos.values()) - sum([self.datos[i] for i in range(0, 9)]))]

        # Título del cuadro
        qp.setPen(QPen(Qt.black, 5, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
        qp.drawText(QPoint((self.width() - qp.fontMetrics().horizontalAdvance(text)) / 2, 14), text)

        etiqs = ["mm", "Nº sites", "%"]

        # Ponemos las etiquetas de las filas
        first_h = 35
        total_h = first_h
        ancho_etq = qp.fontMetrics().horizontalAdvance("Nº sites")
        for t in etiqs:
            qp.drawText((ancho_etq - qp.fontMetrics().horizontalAdvance(t)) / 2, total_h, t)
            total_h += qp.fontMetrics().height() + 7

        colores = [Qt.green, Qt.yellow, QColor(255, 136, 30), Qt.red, QColor(200, 0, 0)]
        # Columnas de los datos
        total = sum(self.datos.values()) - self.datos[-1]
        total_w = ancho_etq + 5
        widthcuadro = 220 / self.n
        for i in range(self.n):
            total_h = first_h
            # Dibujamos los rectángulos de colores
            qp.setPen(QPen(Qt.transparent, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
            qp.setBrush(QBrush(colores[i], Qt.SolidPattern))
            qp.setBrush(QBrush(colores[i], Qt.SolidPattern))
            qp.drawRect(total_w, 20, widthcuadro, 20)
            # Las etiquetas de las colummnas
            qp.setPen(QPen(Qt.black, 5, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
            qp.drawText(total_w + widthcuadro / 2 - qp.fontMetrics().horizontalAdvance(d[i]) / 2, total_h, d[i])
            total_h += qp.fontMetrics().height() + 7
            # Cantidades
            qp.drawText(total_w + widthcuadro / 2 - qp.fontMetrics().horizontalAdvance(nsites[i]) / 2, total_h,
                        nsites[i])
            total_h += qp.fontMetrics().height() + 7
            # Porcentajes
            if total != 0:
                pct = str(round(int(nsites[i]) / total * 100, 1))
            else:
                pct = "0.0"
            qp.drawText(total_w + widthcuadro / 2 - qp.fontMetrics().horizontalAdvance(pct) / 2, total_h, pct)
            total_w += widthcuadro


class BarraPorcentajes(QWidget):
    def __init__(self, datos, n, parent=None):
        super().__init__(parent)
        self.setGeometry(QRect(0, 0, 220, 81))
        self.porcentaje = 0
        self.datos = aplanar_lista(datos)
        self.tipo = n

    def minimumSizeHint(self):
        return QSize(1, 1)

    def actualizarPorcentajes(self, indice, nuevo):
        self.datos[indice] = nuevo
        self.porcentaje = (sum(self.datos)) / len(self.datos)
        self.update()

    def paintEvent(self, event):
        self.setMinimumSize(220, 100)
        # Pintamos un rectángulo con un % pintado
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        width = 220
        w_coloreado = int(width * self.porcentaje)

        qp.setBrush(QBrush(QColor(220, 220, 220), Qt.SolidPattern))
        if self.tipo == 1:
            # Sangrado
            tit = "BOP"
            color = Qt.red
        elif self.tipo == 2:
            # Placa
            tit = "BPL"
            color = QColor(88, 96, 255)
        else:  # tipo = 3
            # Supuración
            tit = "SUP"
            color = QColor(124, 235, 160)

        qp.setPen(QPen(color, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
        # Rectángulo vacío
        qp.drawRect(0, 20, width, 20)
        qp.setBrush(QBrush(color, Qt.SolidPattern))

        # Rectángulo coloreado
        if w_coloreado > 0:
            qp.drawRect(0, 20, w_coloreado, 20)

        # Porcentajes
        txt = "Nº sites = " + str(sum(aplanar_lista(self.datos))) + "; % = " + str(
            round(self.porcentaje * 100, 2)) + "%"

        # Título y porcentajes
        qp.setPen(QPen(Qt.black, 5, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
        qp.drawText(QPoint((self.width() - qp.fontMetrics().horizontalAdvance(tit)) / 2, 14), tit)
        qp.drawText(
            QPoint((self.width() - qp.fontMetrics().horizontalAdvance(txt)) / 2, qp.fontMetrics().height() + 45), txt)


class Datos():
    def __init__(self):
        self.sangrados = [[False, False, False] for _ in range(16)]
        self.placas = [[False, False, False] for _ in range(16)]
        self.supuraciones = [[False, False, False] for _ in range(16)]
        self.margenes = [[0, 0, 0] for _ in range(16)]
        self.profundidades = [[0, 0, 0] for _ in range(16)]
        self.defectosfurca = [0] * 16
        self.implantes = [False] * 16
        self.movilidad = [0] * 16
        self.desactivados = []
        self.inicializados = []

    def extraerDatos(self):
        data = {}
        for i in range(len(dientes)):
            diente = dientes[i]
            if diente not in self.desactivados:
                data[int(diente)] = [self.movilidad[i], self.implantes[i], self.defectosfurca[i], self.sangrados[i],
                                     self.placas[i], self.supuraciones[i], self.margenes[i], self.profundidades[i]]
        df = pd.DataFrame(data)
        df.index = ["Movilidad", "Implante", "Defecto de furca", "Sangrado al sondaje", "Placa", "Supuración",
                    "Margen gingival", "Profundidad de sondaje"]
        df.to_excel(os.path.join(basedir, "./excel/datos" + datetime.datetime.now().strftime("%y%m%d%H%M%S") + ".xlsx"))

    def actualizar_movilidad(self, diente, valor):
        self.movilidad[int(diente)] = abs(int(valor))
        if int(diente) not in self.inicializados:
            self.inicializados.append(int(diente))

    def actualizar_implante(self, diente, valor):
        self.implantes[int(diente)] = valor
        if int(diente) not in self.inicializados:
            self.inicializados.append(int(diente))

    def actualizar_defecto_furca(self, diente, valor):
        self.defectosfurca[int(diente)] = abs(int(valor))
        if int(diente) not in self.inicializados:
            self.inicializados.append(int(diente))

    def actualizar_sangrado(self, diente, i, valor):
        self.sangrados[int(diente)][i] = valor
        if int(diente) not in self.inicializados:
            self.inicializados.append(int(diente))
        window.clasificacion.actualizar()

    def actualizar_placa(self, diente, i, valor):
        self.placas[int(diente)][i] = valor
        if int(diente) not in self.inicializados:
            self.inicializados.append(int(diente))

    def actualizar_supuracion(self, diente, i, valor):
        self.supuraciones[int(diente)][i] = valor
        if int(diente) not in self.inicializados:
            self.inicializados.append(int(diente))

    def actualizar_margen(self, diente, i, valor):
        self.margenes[int(diente)][i] = abs(int(valor))
        if int(diente) not in self.inicializados:
            self.inicializados.append(int(diente))
        window.clasificacion.actualizar()

    def actualizar_profundidad(self, diente, i, valor):
        self.profundidades[int(diente)][i] = abs(int(valor))
        if int(diente) not in self.inicializados:
            self.inicializados.append(int(diente))
        window.clasificacion.actualizar()

    def actualizar_desactivados(self, diente):
        if diente in self.desactivados:
            self.desactivados.remove(diente)
        else:
            self.desactivados.append(diente)


# if periodontitis
def calcular_estadio(cal, datos):
    # No se consideran dientes perdidos
    maxpd = max(aplanar_abs_lista(datos.profundidades))
    # if len(datos.desactivados) == 0:
    if 1 <= cal <= 2:
        if maxpd <= 4:
            return "Stage I"
    elif 3 <= cal <= 4:
        if maxpd <= 5:
            return "Stage II"
    else:  # >= 5
        if maxpd >= 6:
            n_afectacionfurca = sum(1 for elemento in datos.furcas if elemento > 1)
            if n_afectacionfurca >= 1:
                if len(datos.desactivados) < 2:  # Cantidad de dientes totales >= 20
                    # if no colapso de mordida / disfuncion masticatoria
                    return "Stage III"
                # if colapso de mordida / disfuncion masticatoria
                return "Stage IV"
    return "??"


def clasificacion_esquema1(datos):
    # Calcular sangrado medio
    pd = int(sum(aplanar_abs_lista(datos.profundidades)) / len(aplanar_abs_lista(datos.profundidades)))
    bop = sum(aplanar_lista(datos.sangrados)) / len(aplanar_lista(datos.sangrados))
    margen = sum(aplanar_abs_lista(datos.margenes)) / len(aplanar_abs_lista(datos.margenes))
    # calcular rbl/cal
    cal = int((pd + margen) - 2)

    if pd <= 3:
        if bop < 0.1:
            return "SANO"
        if cal == 0:
            return "Gingivitis"
        # if tratamiento periodontal -> "Gingivitis en periodonto reducido"
        # if not tratamiento periodontal
        return calcular_estadio(cal, datos)
    if bop < 0.1:
        if cal == 0:
            return "SANO"
        # if tratamiento periodontal -> "Sano en periodonto reducido"
        if pd == 4:
            return "Sano en periodonto reducido"
        return calcular_estadio(cal, datos)
    if cal == 0:
        return "Gingivitis"
    return calcular_estadio(cal, datos)


class Clasificacion(QLabel):
    def __init__(self, datos):
        super(Clasificacion, self).__init__()
        self.setStyleSheet("font-weight: bold; font-size: 16px; margin-right: 20px;")
        self.setText(clasificacion_esquema1(datos))

    def actualizar(self):
        self.setText(clasificacion_esquema1(window.datos))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.datos = Datos()

        self.setWindowTitle("Periostage")
        self.setStyleSheet("background-color: #ECECEC ")
        self.setMinimumSize(QSize(1000, 500))
        self.resizeEvent = self.actualizar_tam

        self.frameTitulo = QFrame(self)
        self.frameTitulo.setStyleSheet("background-color: white; text-align: center;")
        self.frameTitulo.setGeometry(QRect(0, 0, self.width(), 50))

        self.titulo = QLabel(self.frameTitulo)
        self.titulo.setText("Arcada superior")
        self.titulo.setStyleSheet("font-size: 16pt; font-weight: 350; color: black;")
        self.titulo.adjustSize()
        self.titulo.setGeometry(QRect((self.width() - self.titulo.width()) // 2, 10, self.titulo.width(), self.titulo.height()))

        self.frameColumnasArriba = QFrame(self)
        self.frameColumnasArriba.setGeometry(QRect(0, 50, self.width(), 180))
        self.frameColumnasArriba.setStyleSheet("background-color: grey")

        self.frameEtiquetas = QFrame(self.frameColumnasArriba)
        self.frameEtiquetas.setGeometry(QRect(25, 20, 126, 160))

        etiquetas = ["Movilidad", "Implante", "Defecto de furca",  "Sangrado al sondaje", "Placa", "Supuración", "Margen Gingival", "Profundidad de sondaje"]
        incrementoHeight = 0
        for n in etiquetas:
            label = QLabel(n, self.frameEtiquetas)
            label.setAlignment(Qt.AlignRight)
            label.setGeometry(QRect(0, incrementoHeight, 125, 20))
            incrementoHeight += 20

        incrementoLeft = 175
        for n in range(0, 3):
            Columna(n, True, incrementoLeft, parent=self.frameColumnasArriba)
            incrementoLeft += 45 + 4

        for n in range(3, 8):
            Columna(n, False, incrementoLeft, parent=self.frameColumnasArriba)
            incrementoLeft += 45 + 4
        incrementoLeft += 16

        for n in range(8, 13):
            Columna(n, False, incrementoLeft, parent=self.frameColumnasArriba)
            incrementoLeft += 45 + 4

        for n in range(13, 16):
            Columna(n, True, incrementoLeft, parent=self.frameColumnasArriba)
            incrementoLeft += 45 + 4

        self.frameDatosMedios = QFrame(self)
        self.frameDatosMedios.setGeometry(0, 425, self.width(), 100)
        self.setStyleSheet("background-color: violet")

        self.clasificacion = Clasificacion(self.datos)
        self.clasificacion.setStyleSheet("font-weight: bold; font-size: 16px; margin-right: 20px;")
        self.ppd = CuadroColores(self.datos.profundidades, None, 5, self.frameDatosMedios)
        self.cal = CuadroColores(self.datos.profundidades, self.datos.margenes, 4, self.frameDatosMedios)
        self.sangrado = BarraPorcentajes(self.datos.sangrados, 1)
        self.placa = BarraPorcentajes(self.datos.placas, 2)

        self.frameDibujoDientes = QFrame(self)
        self.frameDibujoDientes.setGeometry(QRect(176, 235, self.width() - 176, 156))
        self.frameDibujoDientes.setStyleSheet("background-color: blue")

    def actualizar_tam(self, event):
        self.frameTitulo.setGeometry(QRect(0, 0, self.width(), 60))
        self.titulo.setGeometry(QRect((self.width() - self.titulo.width()) // 2, 10, self.titulo.width(), self.titulo.height()))
        self.frameColumnasArriba.setGeometry(QRect(0, 60, self.width(), 180))
        self.frameDibujoDientes.setGeometry(QRect(176, 250, self.width() - 176, 156))



app = QApplication(sys.argv)
# app.setWindowIcon(QtGui.QIcon(f"C:/Users/Uxi/Documents/TFG/MasPruebas/diente.ico"))
app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, 'diente.ico')))
window = None
window = MainWindow()
window.showMaximized()
window.show()
app.exec()
