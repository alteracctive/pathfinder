import tkinter as tk
import time
import math
from tkinter import ttk
from tkinter import messagebox
from ctypes import windll  # fix blurry
from collections import defaultdict
import sys
import os

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# Graph data structure
class Graph():
    def __init__(self):
        self.edges = defaultdict(list)
        self.weights = {}
    
    def add_edge(self, from_node, to_node, weight):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.weights[(from_node, to_node)] = weight
        self.weights[(to_node, from_node)] = weight


# Initializing window
window = tk.Tk()
try:
    windll.shcore.SetProcessDpiAwareness(1)  # fix blurry
except:
    pass

window.title('Pathseeker by Altah')
try:
    window.iconbitmap(resource_path("icons/icon.ico"))
except:
    pass

window.state("zoomed")

# Style
style = ttk.Style()
style.map('design1.Toolbutton', 
          background=[('selected', 'red'), ('!disabled', 'light gray')], 
          foreground=[('selected', 'blue'), ('active', 'cyan'), ('!disabled', 'dark red')], 
          font=[('selected', 'calibri 17 bold'), ('!disabled', 'calibri 17')])
style.map('design1.TMenubutton',
          background=[('selected', 'white'), ('!disabled', 'light gray')], 
          foreground=[('selected', 'blue'), ('active', 'cyan'), ('!disabled', 'dark red')], 
          font=[('selected', 'calibri 17 bold'), ('!disabled', 'calibri 17')])

# Global variables
graph = Graph()

# Customization
mazeWidth = 1800
mazeHeight = 900
cellSize = 36
Color_MazeBackground = 'gray17'
Color_SelectedCells = 'lightblue1'
Color_NonSelectedCells = 'gray10'
Color_GridLine = 'gray27'
Color_Line_Border = 'red'
Color_Line_Vertex = 'magenta'
Color_Line_Path = 'goldenrod1'
Color_Line_PathPoint = 'sienna1'
Color_Line_Solution = 'lightslateblue'
Color_PointStart = 'forestgreen'
Color_PointEnd = 'brown3'
pointSize = 4

# Variables
numRow = int(mazeHeight / cellSize)
numColumn = int(mazeWidth / cellSize)
selectedCell = [[0] * (numColumn + 1) for i in range(numRow + 1)]
cellRectangles = {}
mazeVertex = []
deadVertex = []
mazePath = []
allPath = []
penState = tk.StringVar(value='Maze')
mouseSecondary = tk.IntVar(value=0)
MazeSecondary = 0
PointSecondary = 0
mouseTrace = tk.IntVar(value=0)
showGrid = tk.IntVar(value=1)
showVertex = tk.IntVar(value=0)
showPath = tk.IntVar(value=0)  
showBorder = tk.IntVar(value=0)
showSolution = tk.IntVar(value=0)
fastCalc = tk.IntVar(value=1)  
lastMouseX, lastMouseY = 0, 0
lastCellRow, lastCellColumn = -1, -1
startPointX, startPointY, endPointX, endPointY = -1, -1, -1, -1
mouseNum = 0
archiveTimer_Solution = []
archiveTimer_Path = []
lastArchiveTimer_Path = 0
isDragging = False
needsRedraw = False
redrawScheduled = False

# Load images
def load_image(path, default_size=4):
    try:
        return tk.PhotoImage(file=resource_path(path)).subsample(default_size)
    except:
        placeholder = tk.PhotoImage(width=32, height=32)
        return placeholder

Img_Mode_Maze = load_image('icons/Mode_Maze.png')
Img_Mode_Point = load_image('icons/Mode_Point.png')
Img_Maze_SelectAll = load_image('icons/Maze_SelectAll.png')
Img_Maze_UnselectAll = load_image('icons/Maze_UnselectAll.png')
Img_Maze_SelectCell = load_image('icons/Maze_SelectCell.png')
Img_Maze_UnselectCell = load_image('icons/Maze_UnselectCell.png')
Img_Debug_MouseTrace = load_image('icons/Debug_MouseTrace.png')
Img_Debug_showBorder = load_image('icons/Debug_showBorder.png')
Img_Debug_showGrid = load_image('icons/Debug_showGrid.png')
Img_Debug_showPath = load_image('icons/Debug_showPath.png')
Img_Debug_showSolution = load_image('icons/Debug_showSolution.png')
Img_Debug_showVertex = load_image('icons/Debug_showVertex.png')
Img_Point_Start = load_image('icons/Point_Start.png')
Img_Point_End = load_image('icons/Point_End.png')
Img_Point_IncreaseSize = load_image('icons/Point_IncreaseSize.png')
Img_Point_DecreaseSize = load_image('icons/Point_DecreaseSize.png')


# Button modes
def changeMode():
    global penState
    if penState.get() == 'Point':
        Maze_SelectAllButton.place_forget()
        Maze_UnselectAllButton.place_forget()
        Maze_FirstActionButton.place_forget()
        Maze_SecondaryActionButton.place_forget()
        Point_FirstActionButton.place(x=100, y=10)
        Point_SecondaryActionButton.place(x=150, y=10)
        Point_IncreaseSizeButton.place(x=250, y=10)
        Point_DecreaseSizeButton.place(x=300, y=10)
        mouseSecondary.set(PointSecondary)
    elif penState.get() == 'Maze':
        Maze_FirstActionButton.place(x=100, y=10)
        Maze_SecondaryActionButton.place(x=150, y=10)
        Maze_SelectAllButton.place(x=250, y=10)
        Maze_UnselectAllButton.place(x=300, y=10)
        Point_FirstActionButton.place_forget()
        Point_SecondaryActionButton.place_forget()
        Point_IncreaseSizeButton.place_forget()
        Point_DecreaseSizeButton.place_forget()
        mouseSecondary.set(MazeSecondary)


# Frames
FrameMode = tk.Frame(master=window, bg='white', bd=1, relief='sunken', height=100, width=50)
FrameMode.place(x=5, y=5)

FrameTool = tk.Frame(master=window, bg='white', bd=1, relief='sunken', height=100, width=350)
FrameTool.place(x=95, y=5)

FrameDebug = tk.Frame(master=window, bg='white', bd=1, relief='sunken', height=100, width=150)
FrameDebug.place(x=495, y=5)

# Mode buttons
MazeModeButton = ttk.Radiobutton(master=window, image=Img_Mode_Maze, command=lambda: changeMode(),
                                  style='design1.Toolbutton', variable=penState, value='Maze')
MazeModeButton.place(x=10, y=10)

PointModeButton = ttk.Radiobutton(master=window, image=Img_Mode_Point, command=lambda: changeMode(),
                                   style='design1.Toolbutton', variable=penState, value='Point')
PointModeButton.place(x=10, y=60)


def setMouseSecondary():
    global mouseSecondary, MazeSecondary, PointSecondary
    if penState.get() == 'Point':
        PointSecondary = mouseSecondary.get()
    elif penState.get() == 'Maze':
        MazeSecondary = mouseSecondary.get()


def updateCellVisual(row, column):
    """Update a single cell's visual appearance using itemconfig for performance"""
    global cellRectangles, selectedCell
    
    xCell, yCell = column * cellSize, row * cellSize
    cell_key = (row, column)
    
    color = Color_SelectedCells if selectedCell[row][column] == 1 else Color_NonSelectedCells
    
    if cell_key in cellRectangles:
        maze.itemconfig(cellRectangles[cell_key], fill=color)
    else:
        rect_id = maze.create_rectangle(xCell, yCell, xCell + cellSize, yCell + cellSize, 
                                        fill=color, outline='', tags='Cell')
        cellRectangles[cell_key] = rect_id
        maze.tag_lower('Cell')


def bresenhamLine(x0, y0, x1, y1):
    """Generate all cells along a line from (x0, y0) to (x1, y1) using Bresenham's algorithm"""
    cells = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    while True:
        cells.append((y0, x0))
        
        if x0 == x1 and y0 == y1:
            break
            
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    
    return cells


def MassSelected(x):
    global selectedCell, numRow, numColumn, startPointX, startPointY, endPointX, endPointY
    global cellRectangles, lastCellRow, lastCellColumn
    
    colorState = Color_NonSelectedCells
    if x == 1:
        colorState = Color_SelectedCells
    lastCellRow, lastCellColumn = -1, -1
    selectedCell = [[x] * (numColumn + 1) for i in range(numRow + 1)]
    
    for a in range(numRow):
        selectedCell[a][numColumn] = 0
    for a in range(numColumn + 1):
        selectedCell[numRow][a] = 0
    
    maze.delete('all')
    cellRectangles.clear()
    
    if x == 1:
        for row in range(numRow):
            for column in range(numColumn):
                xCell, yCell = column * cellSize, row * cellSize
                rect_id = maze.create_rectangle(xCell, yCell, xCell + cellSize, yCell + cellSize, 
                                              fill=colorState, outline='', tags='Cell')
                cellRectangles[(row, column)] = rect_id
        
        if startPointX != -1 and startPointY != -1:
            maze.create_oval(startPointX + pointSize, startPointY + pointSize, 
                           startPointX - pointSize, startPointY - pointSize, 
                           fill=Color_PointStart, tags='Start')
        if endPointX != -1 and endPointY != -1:
            maze.create_oval(endPointX + pointSize, endPointY + pointSize, 
                           endPointX - pointSize, endPointY - pointSize, 
                           fill=Color_PointEnd, tags='End')
    else:
        startPointX, startPointY, endPointX, endPointY = -1, -1, -1, -1
    
    maze.tag_lower('Cell')
    drawGrid()
    drawLine()
    drawLine(optimizeMode=1)


# Controller board
Maze_SelectAllButton = ttk.Button(master=window, image=Img_Maze_SelectAll, 
                                   command=lambda: MassSelected(1), style='design1.Toolbutton')

Maze_UnselectAllButton = ttk.Button(master=window, image=Img_Maze_UnselectAll, 
                                     command=lambda: MassSelected(0), style='design1.Toolbutton')

Maze_FirstActionButton = ttk.Radiobutton(master=window, image=Img_Maze_SelectCell, 
                                          command=(lambda: setMouseSecondary()),
                                          style='design1.Toolbutton', variable=mouseSecondary, value=0)

Maze_SecondaryActionButton = ttk.Radiobutton(master=window, image=Img_Maze_UnselectCell, 
                                              command=lambda: setMouseSecondary(),
                                              style='design1.Toolbutton', variable=mouseSecondary, value=1)

Point_FirstActionButton = ttk.Radiobutton(master=window, image=Img_Point_Start, 
                                           command=(lambda: setMouseSecondary()),
                                           style='design1.Toolbutton', variable=mouseSecondary, value=0)

Point_SecondaryActionButton = ttk.Radiobutton(master=window, image=Img_Point_End, 
                                               command=lambda: setMouseSecondary(),
                                               style='design1.Toolbutton', variable=mouseSecondary, value=1)


def changePointSize(diff=0):
    global pointSize, startPointX, startPointY, endPointX, endPointY
    pointSize += diff
    if pointSize > 9:
        pointSize = 9
    if pointSize < 1:
        pointSize = 1
    maze.delete('Point')
    if startPointX != -1 and startPointY != -1:
        maze.create_oval(startPointX + pointSize, startPointY + pointSize, 
                        startPointX - pointSize, startPointY - pointSize, 
                        fill=Color_PointStart, tags=['Point', 'Start'])
    if endPointX != -1 and endPointY != -1:
        maze.create_oval(endPointX + pointSize, endPointY + pointSize, 
                        endPointX - pointSize, endPointY - pointSize, 
                        fill=Color_PointEnd, tags=['Point', 'End'])


Point_IncreaseSizeButton = ttk.Button(master=window, image=Img_Point_IncreaseSize, 
                                       command=lambda: changePointSize(1), style='design1.Toolbutton')

Point_DecreaseSizeButton = ttk.Button(master=window, image=Img_Point_DecreaseSize, 
                                       command=lambda: changePointSize(-1), style='design1.Toolbutton')

# Maze visualization
Debug_RenderGridButton = ttk.Checkbutton(master=window, image=Img_Debug_showGrid, 
                                          style='design1.Toolbutton', command=lambda: drawGrid(),
                                          variable=showGrid, onvalue=1, offvalue=0)
Debug_RenderGridButton.place(x=500, y=10)

Debug_MouseTracerButton = ttk.Checkbutton(master=window, image=Img_Debug_MouseTrace, 
                                           style='design1.Toolbutton', variable=mouseTrace, 
                                           onvalue=1, offvalue=0)
Debug_MouseTracerButton.place(x=550, y=10)

Debug_BorderVertexButton = ttk.Checkbutton(master=window, image=Img_Debug_showVertex, 
                                            style='design1.Toolbutton', command=lambda: drawLine(),
                                            variable=showVertex, onvalue=1, offvalue=0)
Debug_BorderVertexButton.place(x=600, y=10)

Debug_BorderLineButton = ttk.Checkbutton(master=window, image=Img_Debug_showBorder, 
                                          style='design1.Toolbutton', command=lambda: drawLine(),
                                          variable=showBorder, onvalue=1, offvalue=0)
Debug_BorderLineButton.place(x=500, y=60)

Debug_BorderPathButton = ttk.Checkbutton(master=window, image=Img_Debug_showPath, 
                                          style='design1.Toolbutton', command=lambda: drawLine(),
                                          variable=showPath, onvalue=1, offvalue=0)
Debug_BorderPathButton.place(x=550, y=60)

Debug_SolutionButton = ttk.Checkbutton(master=window, image=Img_Debug_showSolution, 
                                        style='design1.Toolbutton', 
                                        command=lambda: [drawLine(), drawLine(optimizeMode=1)],
                                        variable=showSolution, onvalue=1, offvalue=0)
Debug_SolutionButton.place(x=600, y=60)

Debug_FastCalcButton = ttk.Checkbutton(master=window, text='FastCalc', 
                                        style='design1.Toolbutton', command=lambda: drawLine(),
                                        variable=fastCalc, onvalue=1, offvalue=0)
Debug_FastCalcButton.place(x=650, y=60)

# Statistics
numberVertex = ttk.Label(window, text='Number of vertices: ' + str(len(mazeVertex)))
numberVertex.place(x=800, y=10)

numberEdge = ttk.Label(window, text='')
numberEdge.place(x=800, y=30)

numberPath = ttk.Label(window, text='')
numberPath.place(x=800, y=50)

timerProcessing_Path = ttk.Label(window, text='')
timerProcessing_Path.place(x=1000, y=10)

timerProcessing_Solution = ttk.Label(window, text='')
timerProcessing_Solution.place(x=1000, y=30)


# Helper functions for grid dimension display
def cellSizeToDimensions(size):
    """Convert cell size to grid dimensions string"""
    cols = int(mazeWidth / size)
    rows = int(mazeHeight / size)
    return f"{cols} x {rows}"


def dimensionsToCellSize(dimensions_str):
    """Convert dimensions string back to cell size"""
    cols = int(dimensions_str.split(' x ')[0])
    return int(mazeWidth / cols)


# Grid size customization
def resizeGrid(dimensions_str):
    global cellSize, numRow, numColumn, selectedCell, penState, mazeHeight, mazeWidth
    global startPointX, startPointY, endPointX, endPointY
    global cellRectangles, lastCellRow, lastCellColumn
    
    new_cellSize = dimensionsToCellSize(dimensions_str)
    
    if new_cellSize != cellSize:
        answer = tk.messagebox.askokcancel(title='Resize grid',
                                          message='By resizing the grid, you will clear everything in the grid')
    else:
        answer = True
    
    if answer:
        lastCellRow, lastCellColumn = -1, -1
        cellSize = new_cellSize
        numRow = int(mazeHeight / cellSize)
        numColumn = int(mazeWidth / cellSize)
        selectedCell = [[0] * (numColumn + 1) for i in range(numRow + 1)]
        cellRectangles.clear()
        maze.delete('all')
        drawGrid()
        maze.tag_raise('outline')
        penState.set('Maze')
        startPointX, startPointY, endPointX, endPointY = -1, -1, -1, -1
        changeMode()
    else:
        varCellDimensions.set(cellSizeToDimensions(cellSize))


# Available cell sizes (20 and above)
availableCellSizes = [20, 25, 30, 36, 45, 50, 60]
dimensionOptions = [cellSizeToDimensions(size) for size in availableCellSizes]

varCellDimensions = tk.StringVar(value=cellSizeToDimensions(cellSize))
cellSizeSelector = ttk.OptionMenu(window, varCellDimensions, cellSizeToDimensions(cellSize), 
                                  *dimensionOptions, command=resizeGrid, 
                                  style='design1.TMenubutton')
cellSizeSelector.place(x=1830, y=5)

# Canvas
brg = tk.Canvas(master=window, height=mazeHeight + 40, width=mazeWidth + 40, bg=Color_MazeBackground)
brg.place(x=30, y=100)

maze = tk.Canvas(master=brg, height=mazeHeight, width=mazeWidth, bg=Color_NonSelectedCells, 
                 border=0, borderwidth=0, highlightbackground="black", highlightthickness=0)
maze.place(relx=0.5, rely=0.5, anchor='center')


def drawGrid():
    maze.delete('gridLine')
    global showGrid
    if showGrid.get() == 1:
        for a in range(cellSize, mazeWidth, cellSize):
            maze.create_line(a, 0, a, mazeHeight, fill=Color_GridLine, tags='gridLine')
        for b in range(cellSize, mazeHeight, cellSize):
            maze.create_line(0, b, mazeWidth, b, fill=Color_GridLine, tags='gridLine')
        maze.create_line(0, 0, mazeWidth, 0, fill=Color_GridLine, width=3, tags='gridLine')
        maze.create_line(0, 0, 0, mazeHeight, fill=Color_GridLine, width=3, tags='gridLine')
        maze.create_line(mazeWidth - 1, 0, mazeWidth - 1, mazeHeight, fill=Color_GridLine, width=2, tags='gridLine')
        maze.create_line(0, mazeHeight - 1, mazeWidth, mazeHeight - 1, fill=Color_GridLine, width=2, tags='gridLine')


def scheduleRedraw():
    """Schedule a redraw after a short delay to batch updates during dragging"""
    global redrawScheduled, needsRedraw
    
    if not redrawScheduled and needsRedraw:
        redrawScheduled = True
        window.after(50, performScheduledRedraw)


def performScheduledRedraw():
    """Perform the scheduled redraw"""
    global redrawScheduled, needsRedraw
    
    if needsRedraw:
        drawLine()
        needsRedraw = False
    
    redrawScheduled = False


def drawLine(optimizeMode=0):
    global mazeVertex, deadVertex, showPath, showVertex, showBorder, showSolution
    
    # Show border
    if showBorder.get() == 1 and optimizeMode == 0:
        drawLine_Border()
    elif showBorder.get() == 0:
        maze.delete('line_Border')
        numberEdge.configure(text='')
    
    # Show vertex
    if optimizeMode == 0:
        maze.delete('line_Vertex')
        mazeVertex = []
        deadVertex = []
        
        for row in range(0, numRow):
            for column in range(0, numColumn):
                if selectedCell[row][column] == 1:
                    # When FastCalc is OFF - do full vertex detection (outer + inner)
                    if fastCalc.get() == 0:
                        # Outer Vertex
                        if selectedCell[row - 1][column] == 0 and selectedCell[row][column - 1] == 0 and selectedCell[row - 1][column - 1] == 0:
                            mazeVertex.append([row, column])
                        if selectedCell[row - 1][column] == 0 and selectedCell[row][column + 1] == 0 and selectedCell[row - 1][column + 1] == 0:
                            mazeVertex.append([row, column + 1])
                        if selectedCell[row + 1][column] == 0 and selectedCell[row][column - 1] == 0 and selectedCell[row + 1][column - 1] == 0:
                            mazeVertex.append([row + 1, column])
                        if selectedCell[row + 1][column] == 0 and selectedCell[row][column + 1] == 0 and selectedCell[row + 1][column + 1] == 0:
                            mazeVertex.append([row + 1, column + 1])
                        
                        # Inner Vertex
                        if selectedCell[row - 1][column] == 1 and selectedCell[row][column - 1] == 1 and selectedCell[row - 1][column - 1] == 0:
                            mazeVertex.append([row, column])
                        if selectedCell[row - 1][column] == 1 and selectedCell[row][column + 1] == 1 and selectedCell[row - 1][column + 1] == 0:
                            mazeVertex.append([row, column + 1])
                        if selectedCell[row + 1][column] == 1 and selectedCell[row][column - 1] == 1 and selectedCell[row + 1][column - 1] == 0:
                            mazeVertex.append([row + 1, column])
                        if selectedCell[row + 1][column] == 1 and selectedCell[row][column + 1] == 1 and selectedCell[row + 1][column + 1] == 0:
                            mazeVertex.append([row + 1, column + 1])
                    
                    # When FastCalc is ON - only detect inner vertices (faster)
                    else:
                        # Inner Vertex only
                        if selectedCell[row - 1][column] == 1 and selectedCell[row][column - 1] == 1 and selectedCell[row - 1][column - 1] == 0:
                            mazeVertex.append([row, column])
                        if selectedCell[row - 1][column] == 1 and selectedCell[row][column + 1] == 1 and selectedCell[row - 1][column + 1] == 0:
                            mazeVertex.append([row, column + 1])
                        if selectedCell[row + 1][column] == 1 and selectedCell[row][column - 1] == 1 and selectedCell[row + 1][column - 1] == 0:
                            mazeVertex.append([row + 1, column])
                        if selectedCell[row + 1][column] == 1 and selectedCell[row][column + 1] == 1 and selectedCell[row + 1][column + 1] == 0:
                            mazeVertex.append([row + 1, column + 1])
        
        # Detect dead vertices
        for row in range(0, numRow + 1):
            for column in range(0, numColumn + 1):
                topLeft = selectedCell[row - 1][column - 1] if row > 0 and column > 0 else 0
                topRight = selectedCell[row - 1][column] if row > 0 and column <= numColumn else 0
                bottomLeft = selectedCell[row][column - 1] if row <= numRow and column > 0 else 0
                bottomRight = selectedCell[row][column] if row <= numRow and column <= numColumn else 0
                
                if topLeft == 1 and bottomRight == 1 and topRight == 0 and bottomLeft == 0:
                    deadVertex.append([row, column])
                elif topRight == 1 and bottomLeft == 1 and topLeft == 0 and bottomRight == 0:
                    deadVertex.append([row, column])
        
        if showVertex.get() == 1:
            for i in range(len(mazeVertex)):
                row, column = mazeVertex[i]
                maze.create_oval(column * cellSize - 3, row * cellSize - 3, 
                               column * cellSize + 3, row * cellSize + 3,
                               fill=Color_Line_Vertex, width=0, tags='line_Vertex')
            
            # Draw dead vertices in dark purple
            for i in range(len(deadVertex)):
                row, column = deadVertex[i]
                maze.create_oval(column * cellSize - 3, row * cellSize - 3, 
                               column * cellSize + 3, row * cellSize + 3,
                               fill='#4B0082', width=0, tags='line_Vertex')
    
    # Show path
    if showPath.get() == 0:
        maze.delete('line_Path')
    if showSolution.get() == 0:
        maze.delete('line_Solution')
    if showPath.get() == 1 or showSolution.get() == 1:
        drawLine_Path(optimizeMode)
    else:
        numberPath.configure(text='')
    
    # Print number
    numberVertex.configure(text='Number of vertices: ' + str(len(mazeVertex)))
    maze.tag_raise('line_Path')
    maze.tag_raise('line_Path_Point')
    maze.tag_raise('line_Vertex')
    maze.tag_raise('line_Border')
    maze.tag_raise('line_Solution')
    maze.tag_raise('Start')
    maze.tag_raise('End')


def drawLine_Border():
    maze.delete('line_Border')
    countEdge = 0
    for row in range(0, numRow):
        for column in range(0, numColumn):
            if selectedCell[row][column] == 1:
                if selectedCell[row - 1][column] == 0:
                    countEdge += 1
                    maze.create_line(column * cellSize, row * cellSize, (column + 1) * cellSize, 
                                   row * cellSize, fill=Color_Line_Border, width=2, tags='line_Border')
                if selectedCell[row][column - 1] == 0:
                    countEdge += 1
                    maze.create_line(column * cellSize, row * cellSize, column * cellSize, 
                                   (row + 1) * cellSize, fill=Color_Line_Border, width=2, tags='line_Border')
                if selectedCell[row + 1][column] == 0:
                    countEdge += 1
                    maze.create_line(column * cellSize, (row + 1) * cellSize, (column + 1) * cellSize, 
                                   (row + 1) * cellSize, fill=Color_Line_Border, width=2, tags='line_Border')
                if selectedCell[row][column + 1] == 0:
                    countEdge += 1
                    maze.create_line((column + 1) * cellSize, row * cellSize, (column + 1) * cellSize, 
                                   (row + 1) * cellSize, fill=Color_Line_Border, width=2, tags='line_Border')
                if row == 0:
                    countEdge += 1
                    maze.create_line(column * cellSize, 1, (column + 1) * cellSize, 1, 
                                   fill=Color_Line_Border, width=2, tags='line_Border')
                if column == 0:
                    countEdge += 1
                    maze.create_line(1, row * cellSize, 1, (row + 1) * cellSize, 
                                   fill=Color_Line_Border, width=2, tags='line_Border')
                if row == numRow - 1:
                    countEdge += 1
                    maze.create_line(column * cellSize, mazeHeight - 1, (column + 1) * cellSize, 
                                   mazeHeight - 1, fill=Color_Line_Border, width=2, tags='line_Border')
                if column == numColumn - 1:
                    countEdge += 1
                    maze.create_line(mazeWidth - 1, row * cellSize, mazeWidth - 1, 
                                   (row + 1) * cellSize, fill=Color_Line_Border, width=2, tags='line_Border')
    numberEdge.configure(text='Number of edges: ' + str(countEdge + 1))


def crossesDeadVertex(x0, y0, x1, y1):
    """Check if the path from (x0,y0) to (x1,y1) crosses any dead vertex"""
    global deadVertex
    
    for vertex in deadVertex:
        vRow, vCol = vertex
        vX = vCol
        vY = vRow
        
        dx = x1 - x0
        dy = y1 - y0
        
        if dx == 0 and dy == 0:
            continue
        
        t = max(0, min(1, ((vX - x0) * dx + (vY - y0) * dy) / (dx * dx + dy * dy)))
        nearestX = x0 + t * dx
        nearestY = y0 + t * dy
        
        distance = math.sqrt((vX - nearestX) ** 2 + (vY - nearestY) ** 2)
        
        if distance < 0.01:
            return True
    
    return False


def drawLine_Path(optimizeMode=0):
    Timer_Solution = time.perf_counter()
    pathLength = 0
    
    # Always delete line_Path_Point when recalculating
    maze.delete('line_Path_Point')
    
    if optimizeMode == 0:
        maze.delete('line_Path')
    
    global mazeVertex, mazePath, allPath, showPath, showSolution, graph
    global archiveTimer_Solution, archiveTimer_Path, lastArchiveTimer_Path
    
    allPath = []
    countPath = 0
    
    local_startX, local_startY = round(startPointX / cellSize, 2), round(startPointY / cellSize, 2)
    local_endX, local_endY = round(endPointX / cellSize, 2), round(endPointY / cellSize, 2)
    
    # Show direct line
    if startPointX != -1 and startPointY != -1 and endPointX != -1 and endPointY != -1:
        if legitPath(local_startX, local_startY, local_endX, local_endY, floatMode=1) == True:
            if showPath.get() == 1:
                maze.create_line(startPointX, startPointY, endPointX, endPointY, 
                               fill=Color_Line_PathPoint, width=1, tags=['line_Path', 'line_Path_Point'])
            countPath += 1
            distance = math.sqrt((local_startX - local_endX) ** 2 + (local_startY - local_endY) ** 2)
            allPath.append([-2, -1, distance])
    
    # Line vertex - start point
    if startPointX != -1 and startPointY != -1:
        for i in range(len(mazeVertex)):
            y0, x0 = mazeVertex[i]
            if legitPath(x0, y0, local_startX, local_startY, floatMode=1) == True:
                if showPath.get() == 1:
                    maze.create_line(x0 * cellSize, y0 * cellSize, startPointX, startPointY, 
                                   fill=Color_Line_PathPoint, width=1, tags=['line_Path', 'line_Path_Point'])
                countPath += 1
                distance = math.sqrt((local_startX - x0) ** 2 + (local_startY - y0) ** 2)
                allPath.append([-2, i, distance])
    
    # Line vertex - vertex
    if optimizeMode == 0:
        mazePath = []
        for i in range(len(mazeVertex)):
            y0, x0 = mazeVertex[i]
            for j in range(i + 1, len(mazeVertex)):
                y1, x1 = mazeVertex[j]
                if legitPath(x0, y0, x1, y1) == True:
                    if showPath.get() == 1:
                        maze.create_line(x0 * cellSize, y0 * cellSize, x1 * cellSize, y1 * cellSize,
                                       fill=Color_Line_Path, width=1, tags='line_Path')
                    countPath += 1
                    distance = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
                    mazePath.append([i, j, distance])
    else:
        countPath += len(mazePath)
    
    allPath += mazePath
    
    # Line vertex - end point
    if endPointX != -1 and endPointY != -1:
        for i in range(len(mazeVertex)):
            y0, x0 = mazeVertex[i]
            if legitPath(x0, y0, local_endX, local_endY, floatMode=1) == True:
                if showPath.get() == 1:
                    maze.create_line(x0 * cellSize, y0 * cellSize, endPointX, endPointY, 
                                   fill=Color_Line_PathPoint, width=1, tags=['line_Path', 'line_Path_Point'])
                countPath += 1
                distance = math.sqrt((local_endX - x0) ** 2 + (local_endY - y0) ** 2)
                allPath.append([i, -1, distance])
    
    numberPath.configure(text='Number of paths: ' + str(countPath))
    
    if optimizeMode == 0:
        lastArchiveTimer_Path = time.perf_counter() - Timer_Solution
        timerProcessing_Path.configure(text='Lastest Visibility Time: ' + 
                                      str(round(lastArchiveTimer_Path * 1000, 2)) + ' ms')
    
    if showSolution.get() == 1 and startPointX != -1 and startPointY != -1 and endPointX != -1 and endPointY != -1 and optimizeMode == 1:
        maze.delete('line_Solution')
        graph = Graph()
        for edge in allPath:
            graph.add_edge(*edge)
        
        solutionList = dijsktra(graph, -2, -1)
        
        if len(solutionList) == 0:
            return 0
        
        x0, y0 = startPointX, startPointY
        for i in range(1, len(solutionList)):
            if solutionList[i] == -1:
                x1, y1 = endPointX, endPointY
            else:
                y1, x1 = mazeVertex[solutionList[i]]
                x1 = x1 * cellSize
                y1 = y1 * cellSize
            
            maze.create_line(x0, y0, x1, y1, fill=Color_Line_Solution, width=3, tags='line_Solution')
            pathLength += math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
            x0, y0 = x1, y1
        
        Timer_Solution = time.perf_counter() - Timer_Solution
        archiveTimer_Solution.append(Timer_Solution)
        archiveTimer_Path.append(lastArchiveTimer_Path)
        
        if len(archiveTimer_Solution) > 100:
            archiveTimer_Solution.pop(0)
            archiveTimer_Path.pop(0)
        
        averageTimer_Solution = sum(archiveTimer_Solution) / len(archiveTimer_Solution)
        maxTimer_Solution = max(archiveTimer_Solution)
        
        timerProcessing_Solution.configure(text='Lastest Solution Time: ' + 
                                          str(round(Timer_Solution * 1000, 2)) + ' ms' + '\n' +
                                          'Solution Length: ' + str(round(pathLength / cellSize, 2)) + ' cell')


def dijsktra(graph, initial, end):
    shortest_paths = {initial: (None, 0)}
    current_node = initial
    visited = set()
    
    while current_node != end:
        visited.add(current_node)
        destinations = graph.edges[current_node]
        weight_to_current_node = shortest_paths[current_node][1]
        
        for next_node in destinations:
            weight = graph.weights[(current_node, next_node)] + weight_to_current_node
            if next_node not in shortest_paths:
                shortest_paths[next_node] = (current_node, weight)
            else:
                current_shortest_weight = shortest_paths[next_node][1]
                if current_shortest_weight > weight:
                    shortest_paths[next_node] = (current_node, weight)
        
        next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
        
        if not next_destinations:
            return []
        
        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])
    
    path = []
    while current_node is not None:
        path.append(current_node)
        next_node = shortest_paths[current_node][0]
        current_node = next_node
    
    path = path[::-1]
    return path


def legitPath(x0, y0, x1, y1, floatMode=0):
    # Check if path crosses any dead vertex
    if crossesDeadVertex(x0, y0, x1, y1):
        return False
    
    if (y0 > y1):
        y0, y1 = y1, y0
        x0, x1 = x1, x0
    
    dx = round(x1 - x0, 10)
    dy = round(y1 - y0, 10)
    steps = max(abs(dx), abs(dy))
    
    if dx == 0 and float(x0).is_integer():
        for i in range(int(y1) - int(y0) + int(float(y1).is_integer() == False)):
            if selectedCell[int(y0) + i][int(x0)] == 0 and selectedCell[int(y0) + i][int(x0) - 1] == 0:
                return False
        return True
    
    if dy == 0 and float(y0).is_integer():
        if dx < 0:
            dx = -dx
            x0, x1 = x1, x0
        for i in range(int(x1) - int(x0) + int(float(x1).is_integer() == False)):
            if selectedCell[int(y0)][int(x0) + i] == 0 and selectedCell[int(y0) - 1][int(x0) + i] == 0:
                return False
        return True
    
    if floatMode == 1 and (x0 != x1 or float(x0).is_integer() == False) and (y0 != y1 or float(y0).is_integer() == False):
        xL = float(min(x0, x1))
        xH = float(max(x0, x1))
        yL = float(min(y0, y1))
        yH = float(max(y0, y1))
        
        if int(xL) == int(xH) and int(yL) == int(yH):
            if selectedCell[int(yL)][int(xL)] == 0:
                return False
            return True
        
        if xH.is_integer() == True:
            xH -= 1
        if yH.is_integer() == True:
            yH -= 1
        
        if int(xL) == int(xH) and int(yL) == int(yH):
            if selectedCell[int(yL)][int(xL)] == 0:
                return False
            return True
    
    if floatMode == 1:
        corx0 = int(x0)
        cory0 = int(y0)
        corx1 = int(x1)
        cory1 = int(y1)
        
        if corx0 == corx1 and cory0 == cory1:
            if selectedCell[cory0][corx0] == 0:
                return False
            return True
        
        x0 = float(x0)
        y0 = float(y0)
        x1 = float(x1)
        y1 = float(y1)
        
        if steps == dx:
            if selectedCell[cory0][corx0] == 0:
                return False
            xR = int(x0) + 1
            yR = y0 + dy * ((xR - x0) / dx)
            x0 = xR
            y0 = yR
            
            if x1.is_integer() == False:
                if y1.is_integer() == False:
                    if selectedCell[cory1][corx1] == 0:
                        return False
                else:
                    if selectedCell[cory1 - 1][corx1] == 0:
                        return False
                xR = int(x1)
            else:
                if y1.is_integer() == False:
                    if selectedCell[cory1][corx1 - 1] == 0:
                        return False
                else:
                    if selectedCell[cory1 - 1][corx1 - 1] == 0:
                        return False
                xR = int(x1) - 1
            
            yR = y1 + dy * ((xR - x1) / dx)
            x1 = xR
            y1 = yR
            
            if float(round(y1, 10)).is_integer() == False:
                if selectedCell[int(y1)][int(x1) - 1] == 0 or selectedCell[int(y1)][int(x1)] == 0:
                    return False
        
        elif steps == -dx:
            if x0.is_integer() == False:
                if selectedCell[cory0][corx0] == 0:
                    return False
                xR = int(x0)
            else:
                if selectedCell[cory0][corx0 - 1] == 0:
                    return False
                xR = int(x0) - 1
            
            yR = y0 + dy * ((xR - x0) / dx)
            x0 = xR
            y0 = yR
            
            if y1.is_integer() == False:
                if selectedCell[cory1][corx1] == 0:
                    return False
            else:
                if selectedCell[cory1 - 1][corx1] == 0:
                    return False
            
            xR = int(x1) + 1
            yR = y1 + dy * ((xR - x1) / dx)
            x1 = xR
            y1 = yR
            
            if float(round(y1, 10)).is_integer() == False:
                if selectedCell[int(y1)][int(x1) - 1] == 0 or selectedCell[int(y1)][int(x1)] == 0:
                    return False
        
        elif steps == dy:
            if dx < 0 and x0.is_integer() == True:
                if selectedCell[cory0][corx0 - 1] == 0:
                    return False
            else:
                if selectedCell[cory0][corx0] == 0:
                    return False
            
            yR = int(y0) + 1
            xR = x0 + dx * ((yR - y0) / dy)
            x0 = xR
            y0 = yR
            
            if y0 <= int(y1):
                if y1.is_integer() == False:
                    if x1.is_integer() == False:
                        if selectedCell[cory1][corx1] == 0:
                            return False
                    yR = int(y1)
                else:
                    if x1.is_integer() == False:
                        if selectedCell[cory1 - 1][corx1] == 0:
                            return False
                    yR = int(y1)
                
                xR = x1 + dx * ((yR - y1) / dy)
                
                if float(xR).is_integer() == False and float(y1).is_integer() == False:
                    if selectedCell[int(yR)][int(xR)] == 0 or selectedCell[int(yR) - 1][int(xR)] == 0:
                        return False
                
                x1 = xR
                y1 = yR
            else:
                if float(x1).is_integer():
                    x1 -= 1
                if float(y1).is_integer():
                    y1 -= 1
                if selectedCell[int(y1)][int(x1)] == 0:
                    return False
                return True
        
        x0 = float(round(x0, 10))
        y0 = float(round(y0, 10))
        x1 = float(round(x1, 10))
        y1 = float(round(y1, 10))
        
        if float(x0).is_integer():
            x0 = int(x0)
        if float(y0).is_integer():
            y0 = int(y0)
        if float(x1).is_integer():
            x1 = int(x1)
        if float(y1).is_integer():
            y1 = int(y1)
        
        if x0 == x1 and y0 == y1:
            return True
    
    dx = x1 - x0
    dy = y1 - y0
    steps = int(max(abs(dx), abs(dy)))
    
    xinc = dx / steps
    yinc = dy / steps
    
    x = float(round(x0, 10))
    y = float(round(y0, 10))
    
    for i in range(steps):
        corx = int(x)
        cory = int(y)
        
        if dx == dy:
            if selectedCell[cory][corx] == 0:
                return False
            if dx - int(dx) != 0 and dy - int(dy) != 0:
                if selectedCell[cory + 1][corx] == 0:
                    return False
            if x.is_integer() == False or y.is_integer() == False:
                if selectedCell[cory][corx - 1] == 0:
                    return False
        
        elif dx == -dy:
            if selectedCell[cory][corx - 1] == 0:
                return False
            if dx - int(dx) != 0 and dy - int(dy) != 0:
                if selectedCell[cory + 1][corx] == 0:
                    return False
            if x.is_integer() == False or y.is_integer() == False:
                if selectedCell[cory][corx] == 0:
                    return False
        
        elif steps == abs(dx):
            if round(y, 8).is_integer() == False:
                if selectedCell[cory][corx] == 0:
                    return False
                if int(x) - int(x + xinc) != 0:
                    if selectedCell[cory][corx - 1] == 0:
                        return False
        
        elif steps == dy:
            if round(x, 8).is_integer() == False:
                if selectedCell[cory][corx] == 0:
                    return False
                if int(y) - int(y + yinc) != 0:
                    if selectedCell[cory - 1][corx] == 0:
                        return False
        
        x = round(x + xinc, 10)
        y = round(y + yinc, 10)
    
    return True


def LeftMouseMove(event):
    x, y = maze.winfo_pointerx() - maze.winfo_rootx(), maze.winfo_pointery() - maze.winfo_rooty()
    global mouseNum, startPointX, startPointY, endPointX, endPointY, pointSize
    global lastCellRow, lastCellColumn, isDragging, needsRedraw
    
    if (mouseTrace.get() == 1) and (penState.get() == 'Maze'):
        global lastMouseX, lastMouseY
        maze.create_oval(x - 2, y - 2, x + 2, y + 2, fill='red', tags='debug')
        maze.create_line(lastMouseX, lastMouseY, x, y, fill='red', tags='debug', capstyle='round')
        lastMouseX, lastMouseY = x, y
    
    if (x >= 0) and (y >= 0) and (x <= mazeWidth - 1) and (y <= mazeHeight - 1):
        if (penState.get() == 'Maze'):
            row = int(y / cellSize)
            column = int(x / cellSize)
            
            if lastCellRow != -1 and lastCellColumn != -1 and (row != lastCellRow or column != lastCellColumn):
                cells_to_update = bresenhamLine(lastCellColumn, lastCellRow, column, row)
                
                for cell_row, cell_col in cells_to_update:
                    if 0 <= cell_row < numRow and 0 <= cell_col < numColumn:
                        if selectedCell[cell_row][cell_col] == 0 and mouseSecondary.get() == mouseNum:
                            selectedCell[cell_row][cell_col] = 1
                            updateCellVisual(cell_row, cell_col)
                        elif selectedCell[cell_row][cell_col] == 1 and mouseSecondary.get() != mouseNum:
                            selectedCell[cell_row][cell_col] = 0
                            updateCellVisual(cell_row, cell_col)
            else:
                if selectedCell[row][column] == 0 and mouseSecondary.get() == mouseNum:
                    selectedCell[row][column] = 1
                    updateCellVisual(row, column)
                elif selectedCell[row][column] == 1 and mouseSecondary.get() != mouseNum:
                    selectedCell[row][column] = 0
                    updateCellVisual(row, column)
            
            lastCellRow, lastCellColumn = row, column
            
            needsRedraw = True
            scheduleRedraw()
        
        elif (penState.get() == 'Point'):
            row = int(y / cellSize)
            column = int(x / cellSize)
            
            if selectedCell[row][column] == 1:
                if mouseSecondary.get() == mouseNum:
                    startPointX, startPointY = x, y
                    maze.delete('Start')
                    maze.create_oval(x + pointSize, y + pointSize, x - pointSize, y - pointSize, 
                                   fill=Color_PointStart, tags=['Point', 'Start'])
                else:
                    endPointX, endPointY = x, y
                    maze.delete('End')
                    maze.create_oval(x + pointSize, y + pointSize, x - pointSize, y - pointSize, 
                                   fill=Color_PointEnd, tags=['Point', 'End'])
                drawLine(optimizeMode=1)
    else:
        lastMouseX, lastMouseY = x, y


def LeftMouseUp(event):
    global mouseNum, isDragging, lastCellRow, lastCellColumn, needsRedraw
    
    isDragging = False
    lastCellRow, lastCellColumn = -1, -1
    
    mouseNum = 0 if event.num == 3 else 1
    maze.delete('debug')
    
    if needsRedraw:
        drawLine()
        needsRedraw = False


def LeftMouseDown(event):
    global isDragging, lastCellRow, lastCellColumn
    
    if mouseTrace.get() == 1:
        global lastMouseX, lastMouseY, mouseNum
        lastMouseX, lastMouseY = maze.winfo_pointerx() - maze.winfo_rootx(), maze.winfo_pointery() - maze.winfo_rooty()
    
    mouseNum = 0 if event.num == 1 else 1
    isDragging = True
    
    lastCellRow, lastCellColumn = -1, -1
    
    LeftMouseMove(event)


# Bind mouse events
window.bind("<B1-Motion>", LeftMouseMove)
window.bind("<B3-Motion>", LeftMouseMove)
window.bind("<ButtonRelease-1>", LeftMouseUp)
window.bind("<ButtonRelease-3>", LeftMouseUp)
window.bind("<Button-1>", LeftMouseDown)
window.bind("<Button-3>", LeftMouseDown)

# Set minimum window size
min_width = mazeWidth + 100
min_height = mazeHeight + 200
window.minsize(min_width, min_height)

# Run
changeMode()
resizeGrid(cellSizeToDimensions(cellSize))
window.mainloop()
