import tkinter as tk
import tkinter.ttk as ttk
from dataclasses import dataclass, field

firstFigure = []
secondFigure = []

def readFileAndMakeFigure(fileName, figure): 
    with open(fileName, 'r') as f:
        for line in f:
            lst = []
            strs = line.split()
            for point in strs:
                lst.append(int(point))
            figure.append(lst)

readFileAndMakeFigure('edges_of_figure_1.txt', firstFigure)
readFileAndMakeFigure('edges_of_figure_2.txt', secondFigure)

@dataclass
class Edge:
    figureID   : int = 0
    x1      : int = 0
    y1      : int = 0
    x2      : int = 0
    y2      : int = 0
    active  : bool = False
    id      : int = 0
    next : list = field(default_factory=list)
    prev : list = field(default_factory=list)
    def __init__(self, figureID: str, x1: int, y1: int, x2: int, y2: int, active: bool, id: int):
        self.figureID  = figureID
        self.active = active
        self.id     = id     
        self.next = list([])
        self.prev = list([])
        if x1 > x2:
            self.x1 = x2
            self.y1 = y2
            self.x2 = x1
            self.y2 = y1
        else:
            self.x1 = x1
            self.y1 = y1    
            self.x2 = x2
            self.y2 = y2
    
def processFigure(_firstFigure, _secondFigure, operation):
    # структура класса для работы с ID рёбер у полигонов
    class IDClass:
        currentID : int = 0

        def __init__(self):
            self.currentID = 0

        def getCurrentID(self): 
            return self.currentID
        
        def getNextID(self):
            self.currentID += 1
            return self.currentID
        
        def resetID(self):
            self.currentID = 0

    crossingArray = []  # массив, который содержит в себе пересечения (место пересечений и какие рёбра пересеклись)

    ID = IDClass()

    # переводчик из одних полигонов в другие, которые удобны для дальнейшей работы
    figure1 = {}
    for edge in _firstFigure:
        figure1[ID.getCurrentID()] = Edge(1, edge[0], edge[1], edge[2], edge[3], False, ID.getNextID()) # WARNING - Right side of this line (after "=") processes before left!
    
    figure2 = {}
    for edge in _secondFigure:
        figure2[ID.getCurrentID()] = Edge(2, edge[0], edge[1], edge[2], edge[3], False, ID.getNextID())

    # поиск всех пересечений
    for id, edge in figure1.items():
        for foreignId, foreignEdge in figure2.items():
            if ((edge.x1 - foreignEdge.x2) * (foreignEdge.x1 - edge.x2)) > 0:
                if (edgeCrossingResult := edgeCrossingXY(edge, foreignEdge)) != -1:
                    crossingArray.append(edgeCrossingResult)
   
    # удаляет пересечения, находящиеся в одном месте
    for i in range(1, len(crossingArray) - 1):
        if crossingArray[i]["x"] == crossingArray[i-1]["x"] and crossingArray[i]["x"] == crossingArray[i-1]["x"]:
            del crossingArray[i]

    idSwapMap = {}  # переопределение ID у рёбер

    for crossing in crossingArray:
        # переопределяют связи между пересечениями рёбер
        if crossing["edge1"] in list(idSwapMap.keys()):
            oldID = crossing["edge1"]
            crossing["edge1"] = idSwapMap[oldID]
        elif crossing["edge2"] in list(idSwapMap.keys()):
            oldID = crossing["edge2"]
            crossing["edge2"] = idSwapMap[oldID]

        # обработка V-образных пересечений (первое касается второго)
        if (crossing["x"] == figure1[crossing["edge1"]].x1 and crossing["y"] == figure1[crossing["edge1"]].y1
            ) or (
            crossing["x"] == figure1[crossing["edge1"]].x2 and crossing["y"] == figure1[crossing["edge1"]].y2):
            
            # запоминается сабдивижн рёбер
            try:
                if m := list(idSwapMap.keys())[list(idSwapMap.values()).index(crossing["edge1"])]:
                    idSwapMap[m] = ID.getNextID()
            except ValueError:
                idSwapMap[crossing["edge2"]] = ID.getNextID()

            # разбивается только второе ребро
            figure2[ID.getCurrentID()] = Edge(1, crossing["x"], crossing["y"], figure2[crossing["edge2"]].x1, figure2[crossing["edge2"]].y1, False, ID.getCurrentID())
            
            figure2[crossing["edge2"]].x1 = crossing["x"]
            figure2[crossing["edge2"]].y1 = crossing["y"]

        # обработка V-образных пересечений (второе касается первого)
        elif (crossing["x"] == figure2[crossing["edge2"]].x1 and crossing["y"] == figure2[crossing["edge2"]].y1
            ) or (
            crossing["x"] == figure2[crossing["edge2"]].x2 and crossing["y"] == figure2[crossing["edge2"]].y2):

            # запоминается сабдивижн рёбер
            try:
                if m := list(idSwapMap.keys())[list(idSwapMap.values()).index(crossing["edge1"])]:
                    idSwapMap[m] = ID.getNextID()
            except ValueError:
                idSwapMap[crossing["edge1"]] = ID.getNextID()

            # разбивается только первое ребро
            figure1[ID.getCurrentID()] = Edge(1, crossing["x"], crossing["y"], figure1[crossing["edge1"]].x1, figure1[crossing["edge1"]].y1, False, ID.getCurrentID())

            figure1[crossing["edge1"]].x1 = crossing["x"]
            figure1[crossing["edge1"]].y1 = crossing["y"]
        
        # обработка Х-образных пересечений
        else:
            # запоминается сабдивижн рёбер
            try:
                if m := list(idSwapMap.keys())[list(idSwapMap.values()).index(crossing["edge1"])]:
                    idSwapMap[m] = ID.getNextID()
            except ValueError:
                idSwapMap[crossing["edge1"]] = ID.getNextID()

            # разбиваются оба ребра
            figure1[ID.getCurrentID()] = Edge(1, crossing["x"], crossing["y"], figure1[crossing["edge1"]].x2, figure1[crossing["edge1"]].y2, False, ID.getCurrentID())

            figure1[crossing["edge1"]].x2 = crossing["x"]
            figure1[crossing["edge1"]].y2 = crossing["y"]

            # переопределяют связи между пересечениями рёбер
            try:
                if m := list(idSwapMap.keys())[list(idSwapMap.values()).index(crossing["edge2"])]:
                    idSwapMap[m] = ID.getNextID()
            except ValueError:
                idSwapMap[crossing["edge2"]] = ID.getNextID()

            figure2[ID.getCurrentID()] = Edge(1, crossing["x"], crossing["y"], figure2[crossing["edge2"]].x2, figure2[crossing["edge2"]].y2, False, ID.getCurrentID())

            figure2[crossing["edge2"]].x2 = crossing["x"]
            figure2[crossing["edge2"]].y2 = crossing["y"]

    resultFigure = {} # итоговая фигура

    # орперация AND
    if operation == "AND":
        for id, edge in figure1.items():
            if isPointInFigureV((edge.x1 + edge.x2) / 2, (edge.y1 + edge.y2) / 2, figure2):
                resultFigure[id] = edge
        
        for id, edge in figure2.items():
            if isPointInFigureV((edge.x1 + edge.x2) / 2, (edge.y1 + edge.y2) / 2, figure1):
                resultFigure[id] = edge
    
    # орперация OR
    elif operation == "OR":
        for id, edge in figure1.items():
            if not isPointInFigureV((edge.x1 + edge.x2) / 2, (edge.y1 + edge.y2) / 2, figure2):
                resultFigure[id] = edge
        
        for id, edge in figure2.items():
            if not isPointInFigureV((edge.x1 + edge.x2) / 2, (edge.y1 + edge.y2) / 2, figure1):
                resultFigure[id] = edge
    
    # орперация NOT
    elif operation == "NOT":
        for id, edge in figure1.items():
            if isPointInFigureV((edge.x1 + edge.x2) / 2, (edge.y1 + edge.y2) / 2, figure2):
                resultFigure[id] = edge
        
        for id, edge in figure2.items():
            if not isPointInFigureV((edge.x1 + edge.x2) / 2, (edge.y1 + edge.y2) / 2, figure1):
                resultFigure[id] = edge
    
    # орперация XOR
    elif operation == "XOR":
        for id, edge in figure1.items():
            resultFigure[id] = edge
        
        for id, edge in figure2.items():
            resultFigure[id] = edge    

    # перевод массив рёбер в удобный для отображения   
    convertedResultFigure = [[0 for x in range(4)] for y in range(len(resultFigure))]    
    i = 0
    for id, edge in resultFigure.items():
        convertedResultFigure[i][0] = edge.x1
        convertedResultFigure[i][1] = edge.y1
        convertedResultFigure[i][2] = edge.x2
        convertedResultFigure[i][3] = edge.y2
        i+=1
    return convertedResultFigure    # возвращает точки конечной фигуры

# функция расчёта пересечения рёбер
def edgeCrossingXY(edge1 : Edge, edge2 : Edge):
    if   (((edge2.y2 - edge2.y1)*(edge1.x2 - edge1.x1) - (edge2.x2 - edge2.x1)*(edge1.y2 - edge1.y1)) == 0):
        return -1
    elif (((edge2.y2 - edge2.y1)*(edge1.x2 - edge1.x1) - (edge2.x2 - edge2.x1)*(edge1.y2 - edge1.y1)) > 0):
        if (edge1.x2 - edge1.x1)*(edge1.y1 - edge2.y1) - (edge1.y2 - edge1.y1)*(edge1.x1 - edge2.x1) < 0 or (edge1.x2 - edge1.x1)*(edge1.y1 - edge2.y1) - (edge1.y2 - edge1.y1)*(edge1.x1 - edge2.x1) > ((edge2.y2 - edge2.y1)*(edge1.x2 - edge1.x1) - (edge2.x2 - edge2.x1)*(edge1.y2 - edge1.y1)):
            return -1 # Первый отрезок пересекается за своими границами
        if (edge2.x2 - edge2.x1)*(edge1.y1 - edge2.y1) - (edge2.y2 - edge2.y1)*(edge1.x1 - edge2.x1) < 0 or (edge2.x2 - edge2.x1)*(edge1.y1 - edge2.y1) - (edge2.y2 - edge2.y1)*(edge1.x1 - edge2.x1) > ((edge2.y2 - edge2.y1)*(edge1.x2 - edge1.x1) - (edge2.x2 - edge2.x1)*(edge1.y2 - edge1.y1)):
            return -1 # Второй отрезок пересекается за своими границами
    else:
        if -((edge1.x2 - edge1.x1)*(edge1.y1 - edge2.y1) - (edge1.y2 - edge1.y1)*(edge1.x1 - edge2.x1)) < 0 or -((edge1.x2 - edge1.x1)*(edge1.y1 - edge2.y1) - (edge1.y2 - edge1.y1)*(edge1.x1 - edge2.x1)) > -((edge2.y2 - edge2.y1)*(edge1.x2 - edge1.x1) - (edge2.x2 - edge2.x1)*(edge1.y2 - edge1.y1)):
            return -1 # Первый отрезок пересекается за своими границами
        if -((edge2.x2 - edge2.x1)*(edge1.y1 - edge2.y1) - (edge2.y2 - edge2.y1)*(edge1.x1 - edge2.x1)) < 0 or -((edge2.x2 - edge2.x1)*(edge1.y1 - edge2.y1) - (edge2.y2 - edge2.y1)*(edge1.x1 - edge2.x1)) > -((edge2.y2 - edge2.y1)*(edge1.x2 - edge1.x1) - (edge2.x2 - edge2.x1)*(edge1.y2 - edge1.y1)):
            return -1 # Второй отрезок пересекается за своими границами

    x = edge1.x1 + (((edge2.x2 - edge2.x1) * (edge1.y1 - edge2.y1) - (edge2.y2 - edge2.y1) * (edge1.x1 - edge2.x1)) / ((edge2.y2 - edge2.y1) * (edge1.x2 - edge1.x1) - (edge2.x2 - edge2.x1) * (edge1.y2 - edge1.y1))) * (edge1.x2 - edge1.x1)
    y = edge1.y1 + (((edge2.x2 - edge2.x1) * (edge1.y1 - edge2.y1) - (edge2.y2 - edge2.y1) * (edge1.x1 - edge2.x1)) / ((edge2.y2 - edge2.y1) * (edge1.x2 - edge1.x1) - (edge2.x2 - edge2.x1) * (edge1.y2 - edge1.y1))) * (edge1.y2 - edge1.y1)

    return { "x" : x, "y" : y, "edge1" : edge1.id, "edge2" : edge2.id }     # возвращает информацию о пересечениях

# функция, которая определяет лежит ли точка внутри фигуры
def isPointInFigureV(x, y, figure):
    crossingCount = 0
    for id, edge in figure.items():
        if ((x - edge.x2) * (x - edge.x2)) > 0:
            if edgeCrossingXY(Edge(-1, x, y, x, 0, False, -1), edge) != -1: crossingCount += 1
    
    if crossingCount % 2 == 0:  return False 
    else:                       return True

# запускающая функция (запускает функцию обработки фигуры и вывода на экран)
def processAndDraw(_canvas : tk.Canvas, _firstFigure, _secondFigure, _operation):
    resultFigure = processFigure(_firstFigure, _secondFigure, _operation)
    _canvas.delete("all")
    drawFigure(_canvas, resultFigure, "#cf25f5")

# функция отрисовки фигуры
def drawFigure(_canvas : tk.Canvas, figure, color):
    for edge in figure:
        _canvas.create_line(((edge[0], edge[1]), (edge[2], edge[3])), fill= color, width=2)

# функция отрисовки исходных фигур
def drawOriginalFigures(_canvas):
    _canvas.delete("all")
    drawFigure(_canvas, firstFigure, "#84f5a2")
    drawFigure(_canvas, secondFigure, "#f5848f")

# определение интерфейса
window = tk.Tk()
window.title("Geometry Calculator")
window.geometry("800x600")
window.minsize(width=610, height=510)

canvas = tk.Canvas(window, width=800, height=400, bd=0, bg="white")
canvas.pack(side="bottom", expand=True, fill="both")

buttonsFrame = ttk.Frame(window, border=0)
buttonsFrame.pack(side="top", expand=False, fill="both")

btnORG = ttk.Button(buttonsFrame, text="Show Polygons", command= lambda : drawOriginalFigures(canvas))
btnORG.pack(side="left", expand=False, padx = 10, pady = 10)

btnAND = ttk.Button(buttonsFrame, text="A AND B", command= lambda : processAndDraw(canvas, firstFigure, secondFigure, "AND"))
btnAND.pack(side="left", expand=False, padx = 10, pady = 10)

btnOR = ttk.Button(buttonsFrame, text="A OR B", command= lambda : processAndDraw(canvas, firstFigure, secondFigure, "OR"))
btnOR.pack(side="left", expand=False, padx = 10, pady = 10)

btnNOT = ttk.Button(buttonsFrame, text="A NOT B", command= lambda : processAndDraw(canvas, firstFigure, secondFigure, "NOT"))
btnNOT.pack(side="left", expand=False, padx = 10, pady = 10)

btnTON = ttk.Button(buttonsFrame, text="B NOT A", command= lambda : processAndDraw(canvas, secondFigure, firstFigure, "NOT"))
btnTON.pack(side="left", expand=False, padx = 10, pady = 10)

btnXOR = ttk.Button(buttonsFrame, text="A XOR B", command= lambda : processAndDraw(canvas, firstFigure, secondFigure, "XOR"))
btnXOR.pack(side="left", expand=False, padx = 10, pady = 10)

window.mainloop()
