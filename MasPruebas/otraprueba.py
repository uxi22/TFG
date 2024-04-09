import sys

from PIL import Image
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

implantes = []

arriba1 = [[1, 5], [5, 6], [4, 8], [9, 8], [9, 8], [7, 7], [6, 8], [10, 6]]  # del 18 al 11
arriba2 = [[7, 11], [6, 6], [7, 8], [8, 9], [8, 10], [7, 5], [5, 5], [2, 1]]  # del 21 al 28

dientes = [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28]

altura_rojo = [[0, 0, 0] for _ in range(16)]
altura_azul = [[0, 0, 0] for _ in range(16)]

colorBoton = "background-color: #BEBEBE;"
style = "margin: 0.5px; border: 1px solid grey; border-radius: 3px;"


class Input03(QLineEdit):
    def __init__(self, furca=False, widgetDientes=None, numDiente=0):
        super().__init__()
        regex = QRegularExpression("[0-3]")  # Expresión regular que permite solo números
        validator = QRegularExpressionValidator(regex)
        self.setValidator(validator)  # Aplicar la validación al QLineEdit
        self.setAlignment(Qt.AlignCenter)
        self.setPlaceholderText("0")
        if furca:
            self.editingFinished.connect(lambda: self.texto_furca(widgetDientes, numDiente))
        self.setStyleSheet("QLineEdit { " + style + "font-size: 10px; } QLineEdit:focus { border: 1px solid #C3C3C3; }")

    def texto_furca(self, widgetDientes, numDiente):
        widgetDientes.def_furca(numDiente, self.text())


class InputSiNo3(QHBoxLayout):
    def __init__(self, color):
        super(InputSiNo3, self).__init__()

        self.w1 = QPushButton("")
        self.w1.setCheckable(True)
        self.w1.setStyleSheet("QPushButton { " + style + colorBoton + "}" +
                              "QPushButton:hover { background-color: #AAAAAA; }")
        self.w1.setDefault(True)  # Para que se pulsen los botones al darle al Enter
        self.w1.clicked.connect(lambda: cambiar_color(self.w1, color))
        self.addWidget(self.w1)

        self.w2 = QPushButton("")
        self.w2.setCheckable(True)
        self.w2.setStyleSheet(
            "QPushButton { " + style + colorBoton + "} QPushButton:hover { background-color: #AAAAAA; }")
        self.w2.setDefault(True)
        self.w2.clicked.connect(lambda: cambiar_color(self.w2, color))
        self.addWidget(self.w2)

        self.w3 = QPushButton("")
        self.w3.setCheckable(True)
        self.w3.setStyleSheet(
            "QPushButton { " + style + colorBoton + "} QPushButton:hover { background-color: #AAAAAA; }")
        self.w3.setDefault(True)
        self.w3.clicked.connect(lambda: cambiar_color(self.w3, color))
        self.addWidget(self.w3)


def es_numero(texto):
    if len(texto) == 0:
        return False
    if texto[0] in ('-', '+'):
        return texto[1:].isdigit()
    return texto.isdigit()


class Input3(QHBoxLayout):
    def __init__(self, ndiente, tipo, widgetDientes):
        super(Input3, self).__init__()

        regex = QRegularExpression(r"^[+-]?\d{1,2}$")  # Expresión regular que permite solo números
        validator = QRegularExpressionValidator(regex)

        self.w1 = QLineEdit()
        self.w1.setValidator(validator)
        self.addWidget(self.w1)
        self.w1.setStyleSheet(
            "QLineEdit { " + style + "font-size: 10px; } QLineEdit:focus { border: 1px solid #C3C3C3; }")
        self.w1.setPlaceholderText("0")
        self.w1.editingFinished.connect(lambda: self.texto(ndiente, tipo, widgetDientes, self.w1, 0))

        self.w2 = QLineEdit()
        self.w2.setValidator(validator)
        self.addWidget(self.w2)
        self.w2.setStyleSheet(
            "QLineEdit { " + style + "font-size: 10px; } QLineEdit:focus { border: 1px solid #C3C3C3; }")
        self.w2.setPlaceholderText("0")
        self.w2.editingFinished.connect(lambda: self.texto(ndiente, tipo, widgetDientes, self.w2, 1))

        self.w3 = QLineEdit()
        self.w3.setValidator(validator)
        self.addWidget(self.w3)
        self.w3.setStyleSheet(
            "QLineEdit { " + style + "font-size: 10px; } QLineEdit:focus { border: 1px solid #C3C3C3; }")
        self.w3.setPlaceholderText("0")
        self.w3.editingFinished.connect(lambda: self.texto(ndiente, tipo, widgetDientes, self.w3, 2))

    def texto(self, ndiente, tipo, widgetDientes, inpt, num):
        if tipo == 1 and es_numero(self.w1.text()):  # Margen gingival
            if -21 < int(inpt.text()) < 21:
                altura_rojo[int(ndiente)][num] = int(inpt.text())
                widgetDientes.actualizar_alturas(int(ndiente), tipo, num)
                widgetDientes.update()
            else:
                inpt.setText("")
        elif tipo == 2 and es_numero(inpt.text()):  # Profundidad de sondaje
            if 0 < int(inpt.text()) < 21:
                altura_azul[int(ndiente)][num] = int(inpt.text())
                widgetDientes.actualizar_alturas(int(ndiente), tipo, num)
                widgetDientes.update()
            else:
                inpt.setText("")


def cambiar_color(boton, color):
    if boton.isChecked():
        boton.setStyleSheet(style + f"background-color: {color}")
    else:
        boton.setStyleSheet(style + colorBoton)


class Columna(QVBoxLayout):
    def __init__(self, numDiente, defFurca, widgetDientes, frame):
        super(Columna, self).__init__()

        print("alignment", self.alignment())
        print(self.contentsMargins())

        botonNumeroDiente = QPushButton(str(dientes[int(numDiente)]))
        botonNumeroDiente.setCheckable(True)
        botonNumeroDiente.setStyleSheet(style + "background-color: #BEBEBE; font-weight: bold; font-size: 12px;")
        botonNumeroDiente.clicked.connect(lambda: self.desactivar_diente(numDiente, widgetDientes))
        #botonNumeroDiente.setGeometry(0, 0, frame.frameSize().width(), 20)

        self.addWidget(botonNumeroDiente, stretch=0, alignment=Qt.AlignTop)

        # MOVILIDAD
        movilidad = Input03(False)

        # DEFECTO DE FURCA
        if defFurca == 1:
            defFurca = Input03(True, widgetDientes, dientes[int(numDiente)])
        else:
            defFurca = QLabel("")
            defFurca.setFixedSize(76, 22)

        # IMPLANTE
        boton = QPushButton("")
        boton.setCheckable(True)
        boton.setStyleSheet(
            "QPushButton { " + style + " background-color: #BEBEBE; } QPushButton:hover { background-color: #AAAAAA; }")
        boton.setDefault(True)
        boton.clicked.connect(lambda: self.diente_implante(numDiente, boton, widgetDientes, defFurca))

        # SANGRADO AL SONDAJE
        sangrado = InputSiNo3("#FF2B32")

        # PLACA
        placa = InputSiNo3("#5860FF")

        # SUPURACION
        supuracion = InputSiNo3("#7CEBA0")

        # MARGEN GINGIVAL
        margenGingival = Input3(numDiente, 1, widgetDientes)

        # PROFUNDIDAD DE SONDAJE
        profSondaje = Input3(numDiente, 2, widgetDientes)

        # añadimos los elementos
        self.addWidget(movilidad, stretch=0, alignment=Qt.AlignTop)
        self.addWidget(boton, stretch=0, alignment=Qt.AlignTop)
        self.addWidget(defFurca, stretch=0, alignment=Qt.AlignTop)
        self.addLayout(sangrado)
        self.addLayout(placa)
        self.addLayout(supuracion)
        self.addLayout(margenGingival)
        self.addLayout(profSondaje)
        self.addStretch()
        

    def diente_implante(self, numDiente, boton, widgetDientes, deffurca):
        cambiar_color(boton, "#333333")
        if boton.isChecked():
            implantes.append(dientes[int(numDiente)])
        else:
            implantes.remove(dientes[int(numDiente)])
        widgetDientes.actualizar_imagen()
        widgetDientes.def_furca(dientes[int(numDiente)], -1, deffurca.text())
        widgetDientes.update()

    def desactivar_diente(self, numDiente, widgetDientes):
        widgetDientes.desactivar_activar_diente(int(numDiente))
        widgetDientes.update()


class ImagenDiente(QImage):
    def __init__(self, pos1, pos2, d1, pos3, pos4, d2):
        super(ImagenDiente, self).__init__()

        width = 0
        # Añadir imagen del diente
        self.dientes1 = []
        # primer sector
        for i in range(pos1, pos2, d1):
            if i in implantes:
                self.dientes1.append(Image.open(f"./DIENTES/periodontograma-i{i}.png"))
            else:
                self.dientes1.append(Image.open(f"./DIENTES/periodontograma-{i}.png"))
            width += self.dientes1[-1].width

        # segundo sector
        self.dientes2 = []
        for i in range(pos3, pos4, d2):
            if i in implantes:
                self.dientes2.append(Image.open(f"./DIENTES/perdiodontograma-i{i}.png"))
            else:
                self.dientes2.append(Image.open(f"./DIENTES/periodontograma-{i}.png"))
            width += self.dientes2[-1].width

        imagen = Image.new('RGB', (width + 40, 156), 'white')

        position = 5
        for d in self.dientes1:
            imagen.paste(d, (position, 0))
            position += d.width
        position += 30
        for d in self.dientes2:
            imagen.paste(d, (position, 0))
            position += d.width
        self.swap(imagen.toqimage())


class LineasSobreDientes(QWidget):
    def __init__(self, *a):
        super().__init__(*a)
        self.imagen = ImagenDiente(18, 10, -1, 21, 29, 1)  # imagen de los dientes con sus atributos

        # inicializamos las listas de los puntos de las líneas
        self.points = QPointList()
        self.points2 = QPointList()
        self.puntos_furca = QPointList()

        self.dientes_desactivados = []
        self.dientes_furca = {}
        self.furcas = [18, 17, 16, 26, 27, 28]

        triangulos_arriba = [[58, 25], [62, 24], [67, 21], [64, 28], [63, 27], [58, 25]]

        dist = 5
        self.altura = 90
        # Valores iniciales de los puntos de los dientes
        for i, diente_imagen in enumerate(self.imagen.dientes1):
            if dientes[i] in self.furcas:
                self.puntos_furca.append(QPoint(dist + triangulos_arriba[self.furcas.index(dientes[i])][1],
                                                triangulos_arriba[self.furcas.index(dientes[i])][0]))
            dist += arriba1[i][0]
            self.points.append(QPoint(dist, int(self.altura)))  # inicio diente
            self.points2.append(QPoint(dist, int(self.altura)))
            wdiente = diente_imagen.width - arriba1[i][0] - arriba1[i][1]
            self.points.append(QPoint(dist + wdiente // 2, int(self.altura)))
            self.points2.append(QPoint(dist + wdiente // 2, int(self.altura)))
            dist += wdiente
            self.points.append(QPoint(dist, int(self.altura)))  # fin diente, ppio siguiente
            self.points2.append(QPoint(dist, int(self.altura)))
            dist += arriba1[i][1]
        dist += 30

        for i, diente_imagen in enumerate(self.imagen.dientes2):
            if dientes[i + 8] in self.furcas:
                self.puntos_furca.append(QPoint(dist + triangulos_arriba[self.furcas.index(dientes[i + 8])][1],
                                                triangulos_arriba[self.furcas.index(dientes[i + 8])][0]))
            dist += arriba2[i][0]
            self.points.append(QPoint(dist, int(self.altura)))
            self.points2.append(QPoint(dist, int(self.altura)))
            wdiente = diente_imagen.width - arriba2[i][0] - arriba2[i][1]
            self.points.append(QPoint(dist + wdiente // 2, int(self.altura)))
            self.points2.append(QPoint(dist + wdiente // 2, int(self.altura)))
            dist += wdiente
            self.points.append(QPoint(dist, int(self.altura)))
            self.points2.append(QPoint(dist, int(self.altura)))
            dist += arriba2[i][1]

    def paintEvent(self, event):
        qp = QPainter(self)

        # Imagen de los dientes
        imagen = QImage(self.imagen)
        tam = QRect(0, 0, imagen.width(), imagen.height())
        self.setMinimumSize(imagen.width(), imagen.height())
        qp.drawImage(tam, imagen)

        pen = qp.pen()
        pen.setWidth(1.5)
        qp.setPen(pen)
        altura_ini = -5.6

        # Dibujamos las líneas negras horizontales
        for i in range(1, 18):
            altura_ini += 5.6
            qp.drawLine(0, altura_ini, tam.width(), altura_ini)

        qp.setRenderHint(QPainter.Antialiasing, True)

        poligono = QPolygon()
        brush = QBrush(QColor(50, 0, 100, 100))
        qp.setBrush(brush)

        auxpuntos = []

        for i in range(16):
            if i not in self.dientes_desactivados:
                brush = QBrush(QColor(50, 0, 100, 100))
                qp.setBrush(brush)
                qp.setPen(QPen(Qt.blue, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
                auxpuntos.append(self.points2[i * 3])
                auxpuntos.append(self.points2[i * 3 + 1])
                auxpuntos.append(self.points2[i * 3 + 2])
                qp.drawPolyline(auxpuntos)  # línea azul
                poligono.append(auxpuntos)
                qp.setPen(QPen(Qt.red, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
                auxpuntos.clear()
                auxpuntos.append(self.points[i * 3])
                auxpuntos.append(self.points[i * 3 + 1])
                auxpuntos.append(self.points[i * 3 + 2])
                qp.drawPolyline(auxpuntos)  # línea roja
                poligono.append(list(reversed(auxpuntos)))
                qp.setPen(QPen(Qt.NoPen))
                qp.drawPolygon(poligono)
                if (i + 1 not in self.dientes_desactivados) and i != 7 and i != 15:
                    poligono.clear()
                    auxpuntos.clear()
                    qp.setPen(QPen(Qt.blue, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
                    auxpuntos.append(self.points2[i * 3 + 2])
                    auxpuntos.append(self.points2[i * 3 + 3])
                    qp.drawPolyline(auxpuntos)  # línea azul
                    poligono.append(auxpuntos)
                    qp.setPen(QPen(Qt.red, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
                    auxpuntos.clear()
                    auxpuntos.append(self.points[i * 3 + 2])
                    auxpuntos.append(self.points[i * 3 + 3])
                    qp.drawPolyline(auxpuntos)  # línea roja
                    poligono.append(list(reversed(auxpuntos)))
                    qp.setPen(QPen(Qt.NoPen))
                    qp.drawPolygon(poligono)
                qp.setBrush(Qt.NoBrush)
                poligono.clear()
                auxpuntos.clear()

                # defectos de furca
                if len(self.dientes_furca) > 0 and dientes[i] in self.dientes_furca.keys():
                    valor = self.dientes_furca[dientes[i]]
                    qp.setPen(QPen(Qt.darkRed, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
                    auxpuntos = [self.puntos_furca[self.furcas.index(dientes[i])].x(),
                                 self.puntos_furca[self.furcas.index(dientes[i])].y()]
                    (poligono << QPoint(auxpuntos[0] - 10, auxpuntos[1]) <<
                     QPoint(auxpuntos[0], auxpuntos[1] + 15) << QPoint(auxpuntos[0] + 10, auxpuntos[1]))
                    if valor == "1":
                        qp.drawPolyline(poligono)  # triángulo sin cerrar y sin rellenar
                    else:
                        if valor == "3":
                            qp.setBrush(QBrush(Qt.darkRed, Qt.SolidPattern))
                        qp.drawPolygon(poligono)
                    poligono.clear()
                    auxpuntos.clear()

            else:
                # dibujar una línea para tachar el diente
                punto_ini = QPoint(self.points[i * 3 + 2].x(), 0)
                punto_fin = QPoint(self.points[i * 3].x(), self.height())
                qp.setPen(QPen(Qt.black, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))
                qp.drawLine(punto_ini, punto_fin)

    def minimumSizeHint(self):
        return QSize(1, 1)

    def actualizar_imagen(self):
        self.imagen = ImagenDiente(18, 10, -1, 21, 29, 1)

    def desactivar_activar_diente(self, num):
        if num not in self.dientes_desactivados:
            self.dientes_desactivados.append(num)
        else:
            self.dientes_desactivados.remove(num)

    def actualizar_alturas(self, numeroDiente, tipo, indice):
        if tipo == 1:  # Margen gingival
            aux = self.points[numeroDiente * 3 + indice]
            aux.setY(int(self.altura + 5.6 * altura_rojo[numeroDiente][indice]))
            self.points[numeroDiente * 3 + indice] = aux
            aux = self.points2[numeroDiente * 3 + indice]
            aux.setY(int(self.points[numeroDiente * 3 + indice].y() - 5.6 * altura_azul[numeroDiente][indice]))
            self.points2[numeroDiente * 3 + indice] = aux
        elif tipo == 2:  # Profundidad de sondaje
            aux = self.points[numeroDiente * 3 + indice]
            aux.setY(int(self.altura + 5.6 * (altura_rojo[numeroDiente][indice] - altura_azul[numeroDiente][indice])))
            self.points2[numeroDiente * 3 + indice] = aux

    def def_furca(self, numDiente, valor, txt=''):
        if valor == -1:
            if numDiente in self.dientes_furca.keys():
                del self.dientes_furca[numDiente]
            elif txt != '':
                self.dientes_furca[numDiente] = int(txt)
        elif valor != 0:
            self.dientes_furca[numDiente] = valor
        elif numDiente in self.dientes_furca.keys():  # si val = 0 y diente en dientes_Furca
            del self.dientes_furca[numDiente]
        self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Periostage")

        self.setMinimumSize(QSize(1000, 500))

        self.elementos()

    def elementos(self):
        frameTotal = QFrame(self)
        frameTotal.setGeometry(0, 0, self.frameSize().width(), self.frameSize().height())

        # Frame titulo
        frameTitu = QFrame(frameTotal)
        frameTitu.setGeometry(0, 0, self.frameSize().width(), 50)
        titu = QLabel("Arcada superior", parent=frameTitu)
        titu.setAlignment(Qt.AlignCenter)
        titu.setStyleSheet("font-size: 15px; color: black;")
        titu.setGeometry(0, 0, frameTitu.frameSize().width(), frameTitu.frameSize().height())

        # Frame cuadro
        frameCuadro = QFrame(frameTotal)
        frameCuadro.setGeometry(0, 50, self.frameSize().width(), 20*9)

        # Frame columna de las etiquetas
        frameEtiquetas = QFrame(frameCuadro)
        frameEtiquetas.setStyleSheet("padding: 0px; margin: 0px;")
        frameEtiquetas.setGeometry(0, 0, 150, frameCuadro.frameSize().height())
        etiquetas = ["", "Movilidad", "Implante", "Defecto de furca",
                     "Sangrado al sondaje", "Placa", "Supuración", "Margen Gingival", "Profundidad de sondaje"]

        for n in etiquetas:
            etiqueta = QLabel(n, parent=frameEtiquetas)
            etiqueta.setAlignment(Qt.AlignRight)
            etiqueta.setGeometry(0, etiquetas.index(n)*20, frameEtiquetas.frameSize().width(), 20)
            etiqueta.setWordWrap(True)
            etiqueta.setStyleSheet("font-size: 11px; color: black; border: 1px solid grey;")

        # Widget dientes
        widgetDientes = LineasSobreDientes()
        widgetDientes.setParent(frameTotal)
        widgetDientes.setGeometry(frameEtiquetas.width(), frameCuadro.height() + frameTitu.height() + 10, frameTotal.frameSize().width() - frameEtiquetas.width(), widgetDientes.frameSize().height())

        # Columnas
        posicion_y = frameEtiquetas.width()
        framesColumnas = [QFrame(frameCuadro) for _ in range(0, 16)]
        for n in range(0, 3):
            framesColumnas[n].setGeometry(posicion_y, 0, widgetDientes.imagen.dientes1[n].width,
                                 frameEtiquetas.height())
            posicion_y += widgetDientes.imagen.dientes1[n].width
            col = Columna(n, 1, widgetDientes, framesColumnas[n])
            framesColumnas[n].setLayout(col)
            col.setGeometry(QRect(0, 0, framesColumnas[n].width(), framesColumnas[n].height()))
            framesColumnas[n].setStyleSheet("border: 1px solid blue; padding: 0px; margin: 0px;") # cambiar los margenes y espacios


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()