import tkinter as tk
import time
import math
import random
from tkinter import ttk
from tkinter import messagebox
from ctypes import windll  # fix blurry
from collections import defaultdict
import sys
import os
from concurrent.futures import ThreadPoolExecutor
import threading

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

window.title('Pathfinder by Altah')
try:
    window.iconbitmap(resource_path("icons/icon.ico"))
except:
    pass

window.state("zoomed")

# Configure grid weights for proper resizing
window.grid_rowconfigure(0, weight=0)  # Toolbar - fixed size
window.grid_rowconfigure(1, weight=1)  # Canvas - expandable
window.grid_columnconfigure(0, weight=1)  # Full width

# Style
style = ttk.Style()
style.configure('design1.Toolbutton', 
                relief='raised', 
                borderwidth=2)
style.map('design1.Toolbutton', 
          background=[('selected', 'red'), ('!disabled', 'light gray')], 
          foreground=[('selected', 'blue'), ('active', 'cyan'), ('!disabled', 'dark red')], 
          font=[('selected', 'calibri 14 bold'), ('!disabled', 'calibri 14')],
          relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

style.configure('design1.TMenubutton',
                relief='raised',
                borderwidth=2)
style.map('design1.TMenubutton',
          background=[('selected', 'white'), ('!disabled', 'light gray')], 
          foreground=[('selected', 'blue'), ('active', 'cyan'), ('!disabled', 'dark red')], 
          font=[('selected', 'calibri 14 bold'), ('!disabled', 'calibri 14')])

# Global variables
graph = Graph()

# Thread pool for parallel operations
executor = ThreadPoolExecutor(max_workers=4)

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


# ====================
# TOOLBAR SECTION
# ====================

# Main toolbar frame
ToolbarFrame = tk.Frame(master=window, bg='lightgray', relief='raised', bd=2, height=160)
ToolbarFrame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
ToolbarFrame.grid_propagate(False)

# Configure toolbar grid
for i in range(25):
    ToolbarFrame.grid_columnconfigure(i, weight=0)


# Button modes
def changeMode():
    global penState
    if penState.get() == 'Point':
        Maze_SelectAllButton.grid_remove()
        Maze_UnselectAllButton.grid_remove()
        Maze_FirstActionButton.grid_remove()
        Maze_SecondaryActionButton.grid_remove()
        Maze_RandomizeButton.grid_remove()
        Maze_SelectAllLabel.grid_remove()
        Maze_UnselectAllLabel.grid_remove()
        Maze_SelectLabel.grid_remove()
        Maze_UnselectLabel.grid_remove()
        Maze_RandomLabel.grid_remove()
        Point_FirstActionButton.grid()
        Point_SecondaryActionButton.grid()
        Point_IncreaseSizeButton.grid()
        Point_DecreaseSizeButton.grid()
        Point_StartLabel.grid()
        Point_EndLabel.grid()
        Point_IncreaseLabel.grid()
        Point_DecreaseLabel.grid()
        mouseSecondary.set(PointSecondary)
    elif penState.get() == 'Maze':
        Maze_FirstActionButton.grid()
        Maze_SecondaryActionButton.grid()
        Maze_SelectAllButton.grid()
        Maze_UnselectAllButton.grid()
        Maze_RandomizeButton.grid()
        Maze_SelectAllLabel.grid()
        Maze_UnselectAllLabel.grid()
        Maze_SelectLabel.grid()
        Maze_UnselectLabel.grid()
        Maze_RandomLabel.grid()
        Point_FirstActionButton.grid_remove()
        Point_SecondaryActionButton.grid_remove()
        Point_IncreaseSizeButton.grid_remove()
        Point_DecreaseSizeButton.grid_remove()
        Point_StartLabel.grid_remove()
        Point_EndLabel.grid_remove()
        Point_IncreaseLabel.grid_remove()
        Point_DecreaseLabel.grid_remove()
        mouseSecondary.set(MazeSecondary)


# === ROW 0: Section Header ===
ttk.Label(ToolbarFrame, text="Mode:", font=('Calibri', 12, 'bold'), background='lightgray').grid(
    row=0, column=0, padx=5, pady=2, sticky='w')

MazeModeButton = ttk.Radiobutton(master=ToolbarFrame, image=Img_Mode_Maze, command=lambda: changeMode(),
                                  style='design1.Toolbutton', variable=penState, value='Maze')
MazeModeButton.grid(row=1, column=0, padx=5, pady=(2,0))

ttk.Label(ToolbarFrame, text="Maze", font=('Calibri', 9), background='lightgray').grid(
    row=2, column=0, pady=(0,2))

PointModeButton = ttk.Radiobutton(master=ToolbarFrame, image=Img_Mode_Point, command=lambda: changeMode(),
                                   style='design1.Toolbutton', variable=penState, value='Point')
PointModeButton.grid(row=3, column=0, padx=5, pady=(2,0))

ttk.Label(ToolbarFrame, text="Point", font=('Calibri', 9), background='lightgray').grid(
    row=4, column=0, pady=(0,2))

ttk.Separator(ToolbarFrame, orient='vertical').grid(row=0, column=1, rowspan=5, sticky='ns', padx=10)


# === Tools Section ===
ttk.Label(ToolbarFrame, text="Tools:", font=('Calibri', 12, 'bold'), background='lightgray').grid(
    row=0, column=2, padx=5, pady=2, sticky='w')


def setMouseSecondary():
    global mouseSecondary, MazeSecondary, PointSecondary
    if penState.get() == 'Point':
        PointSecondary = mouseSecondary.get()
    elif penState.get() == 'Maze':
        MazeSecondary = mouseSecondary.get()


Maze_FirstActionButton = ttk.Radiobutton(master=ToolbarFrame, image=Img_Maze_SelectCell, 
                                          command=(lambda: setMouseSecondary()),
                                          style='design1.Toolbutton', variable=mouseSecondary, value=0)
Maze_FirstActionButton.grid(row=1, column=2, padx=3, pady=(2,0))

Maze_SelectLabel = ttk.Label(ToolbarFrame, text="Select", font=('Calibri', 9), background='lightgray')
Maze_SelectLabel.grid(row=2, column=2, pady=(0,2))

Maze_SecondaryActionButton = ttk.Radiobutton(master=ToolbarFrame, image=Img_Maze_UnselectCell, 
                                              command=lambda: setMouseSecondary(),
                                              style='design1.Toolbutton', variable=mouseSecondary, value=1)
Maze_SecondaryActionButton.grid(row=1, column=3, padx=3, pady=(2,0))

Maze_UnselectLabel = ttk.Label(ToolbarFrame, text="Unselect", font=('Calibri', 9), background='lightgray')
Maze_UnselectLabel.grid(row=2, column=3, pady=(0,2))

Maze_SelectAllButton = ttk.Button(master=ToolbarFrame, image=Img_Maze_SelectAll, 
                                   command=lambda: MassSelected(1), style='design1.Toolbutton')
Maze_SelectAllButton.grid(row=1, column=4, padx=3, pady=(2,0))

Maze_SelectAllLabel = ttk.Label(ToolbarFrame, text="All", font=('Calibri', 9), background='lightgray')
Maze_SelectAllLabel.grid(row=2, column=4, pady=(0,2))

Maze_UnselectAllButton = ttk.Button(master=ToolbarFrame, image=Img_Maze_UnselectAll, 
                                     command=lambda: MassSelected(0), style='design1.Toolbutton')
Maze_UnselectAllButton.grid(row=1, column=5, padx=3, pady=(2,0))

Maze_UnselectAllLabel = ttk.Label(ToolbarFrame, text="Clear", font=('Calibri', 9), background='lightgray')
Maze_UnselectAllLabel.grid(row=2, column=5, pady=(0,2))

Maze_RandomizeButton = ttk.Button(master=ToolbarFrame, text='Random', 
                                   command=lambda: generateRandomMaze(), style='design1.Toolbutton')
Maze_RandomizeButton.grid(row=1, column=6, padx=3, pady=(2,0))

Maze_RandomLabel = ttk.Label(ToolbarFrame, text="Generate", font=('Calibri', 9), background='lightgray')
Maze_RandomLabel.grid(row=2, column=6, pady=(0,2))

Point_FirstActionButton = ttk.Radiobutton(master=ToolbarFrame, image=Img_Point_Start, 
                                           command=(lambda: setMouseSecondary()),
                                           style='design1.Toolbutton', variable=mouseSecondary, value=0)
Point_FirstActionButton.grid(row=1, column=2, padx=3, pady=(2,0))

Point_StartLabel = ttk.Label(ToolbarFrame, text="Start", font=('Calibri', 9), background='lightgray')
Point_StartLabel.grid(row=2, column=2, pady=(0,2))

Point_SecondaryActionButton = ttk.Radiobutton(master=ToolbarFrame, image=Img_Point_End, 
                                               command=lambda: setMouseSecondary(),
                                               style='design1.Toolbutton', variable=mouseSecondary, value=1)
Point_SecondaryActionButton.grid(row=1, column=3, padx=3, pady=(2,0))

Point_EndLabel = ttk.Label(ToolbarFrame, text="End", font=('Calibri', 9), background='lightgray')
Point_EndLabel.grid(row=2, column=3, pady=(0,2))


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


Point_IncreaseSizeButton = ttk.Button(master=ToolbarFrame, image=Img_Point_IncreaseSize, 
                                       command=lambda: changePointSize(1), style='design1.Toolbutton')
Point_IncreaseSizeButton.grid(row=1, column=4, padx=3, pady=(2,0))

Point_IncreaseLabel = ttk.Label(ToolbarFrame, text="Bigger", font=('Calibri', 9), background='lightgray')
Point_IncreaseLabel.grid(row=2, column=4, pady=(0,2))

Point_DecreaseSizeButton = ttk.Button(master=ToolbarFrame, image=Img_Point_DecreaseSize, 
                                       command=lambda: changePointSize(-1), style='design1.Toolbutton')
Point_DecreaseSizeButton.grid(row=1, column=5, padx=3, pady=(2,0))

Point_DecreaseLabel = ttk.Label(ToolbarFrame, text="Smaller", font=('Calibri', 9), background='lightgray')
Point_DecreaseLabel.grid(row=2, column=5, pady=(0,2))

ttk.Separator(ToolbarFrame, orient='vertical').grid(row=0, column=7, rowspan=5, sticky='ns', padx=10)


# === Display Section ===
ttk.Label(ToolbarFrame, text="Display:", font=('Calibri', 12, 'bold'), background='lightgray').grid(
    row=0, column=8, padx=5, pady=2, sticky='w')

Debug_RenderGridButton = ttk.Checkbutton(master=ToolbarFrame, image=Img_Debug_showGrid, 
                                          style='design1.Toolbutton', command=lambda: drawGrid(),
                                          variable=showGrid, onvalue=1, offvalue=0)
Debug_RenderGridButton.grid(row=1, column=8, padx=3, pady=(2,0))

ttk.Label(ToolbarFrame, text="Grid", font=('Calibri', 9), background='lightgray').grid(
    row=2, column=8, pady=(0,2))

Debug_MouseTracerButton = ttk.Checkbutton(master=ToolbarFrame, image=Img_Debug_MouseTrace, 
                                           style='design1.Toolbutton', variable=mouseTrace, 
                                           onvalue=1, offvalue=0)
Debug_MouseTracerButton.grid(row=1, column=9, padx=3, pady=(2,0))

ttk.Label(ToolbarFrame, text="Trace", font=('Calibri', 9), background='lightgray').grid(
    row=2, column=9, pady=(0,2))

Debug_BorderVertexButton = ttk.Checkbutton(master=ToolbarFrame, image=Img_Debug_showVertex, 
                                            style='design1.Toolbutton', command=lambda: drawLine(),
                                            variable=showVertex, onvalue=1, offvalue=0)
Debug_BorderVertexButton.grid(row=1, column=10, padx=3, pady=(2,0))

ttk.Label(ToolbarFrame, text="Vertices", font=('Calibri', 9), background='lightgray').grid(
    row=2, column=10, pady=(0,2))

Debug_BorderLineButton = ttk.Checkbutton(master=ToolbarFrame, image=Img_Debug_showBorder, 
                                          style='design1.Toolbutton', command=lambda: drawLine(),
                                          variable=showBorder, onvalue=1, offvalue=0)
Debug_BorderLineButton.grid(row=3, column=8, padx=3, pady=(2,0))

ttk.Label(ToolbarFrame, text="Border", font=('Calibri', 9), background='lightgray').grid(
    row=4, column=8, pady=(0,2))

Debug_BorderPathButton = ttk.Checkbutton(master=ToolbarFrame, image=Img_Debug_showPath, 
                                          style='design1.Toolbutton', command=lambda: drawLine(),
                                          variable=showPath, onvalue=1, offvalue=0)
Debug_BorderPathButton.grid(row=3, column=9, padx=3, pady=(2,0))

ttk.Label(ToolbarFrame, text="Paths", font=('Calibri', 9), background='lightgray').grid(
    row=4, column=9, pady=(0,2))

Debug_SolutionButton = ttk.Checkbutton(master=ToolbarFrame, image=Img_Debug_showSolution, 
                                        style='design1.Toolbutton', 
                                        command=lambda: [drawLine(), drawLine(optimizeMode=1)],
                                        variable=showSolution, onvalue=1, offvalue=0)
Debug_SolutionButton.grid(row=3, column=10, padx=3, pady=(2,0))

ttk.Label(ToolbarFrame, text="Solution", font=('Calibri', 9), background='lightgray').grid(
    row=4, column=10, pady=(0,2))

Debug_FastCalcButton = ttk.Checkbutton(master=ToolbarFrame, text='FastCalc', 
                                        style='design1.Toolbutton', command=lambda: drawLine(),
                                        variable=fastCalc, onvalue=1, offvalue=0)
Debug_FastCalcButton.grid(row=3, column=11, padx=3, pady=(2,0))

ttk.Label(ToolbarFrame, text="Quick", font=('Calibri', 9), background='lightgray').grid(
    row=4, column=11, pady=(0,2))

ttk.Separator(ToolbarFrame, orient='vertical').grid(row=0, column=12, rowspan=5, sticky='ns', padx=10)


# === Statistics Section ===
ttk.Label(ToolbarFrame, text="Statistics:", font=('Calibri', 12, 'bold'), background='lightgray').grid(
    row=0, column=13, padx=5, pady=2, sticky='w')

numberVertex = ttk.Label(ToolbarFrame, text='Vertices: 0', font=('Calibri', 10), background='lightgray')
numberVertex.grid(row=1, column=13, padx=5, pady=2, sticky='w')

numberEdge = ttk.Label(ToolbarFrame, text='', font=('Calibri', 10), background='lightgray')
numberEdge.grid(row=2, column=13, padx=5, pady=2, sticky='w')

numberPath = ttk.Label(ToolbarFrame, text='', font=('Calibri', 10), background='lightgray')
numberPath.grid(row=3, column=13, padx=5, pady=2, sticky='w')

timerProcessing_Path = ttk.Label(ToolbarFrame, text='', font=('Calibri', 9), background='lightgray')
timerProcessing_Path.grid(row=1, column=14, padx=5, pady=2, sticky='w')

timerProcessing_Solution = ttk.Label(ToolbarFrame, text='', font=('Calibri', 9), background='lightgray')
timerProcessing_Solution.grid(row=2, column=14, rowspan=2, padx=5, pady=2, sticky='w')

ttk.Separator(ToolbarFrame, orient='vertical').grid(row=0, column=15, rowspan=5, sticky='ns', padx=10)


# === Grid Size Selector ===
ttk.Label(ToolbarFrame, text="Grid:", font=('Calibri', 12, 'bold'), background='lightgray').grid(
    row=0, column=16, padx=5, pady=2, sticky='w')


def cellSizeToDimensions(size):
    """Convert cell size to grid dimensions string"""
    cols = int(mazeWidth / size)
    rows = int(mazeHeight / size)
    return f"{cols} x {rows}"


def dimensionsToCellSize(dimensions_str):
    """Convert dimensions string back to cell size"""
    cols = int(dimensions_str.split(' x ')[0])
    return int(mazeWidth / cols)


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


availableCellSizes = [20, 25, 30, 36, 45, 50, 60]
dimensionOptions = [cellSizeToDimensions(size) for size in availableCellSizes]

varCellDimensions = tk.StringVar(value=cellSizeToDimensions(cellSize))
cellSizeSelector = ttk.OptionMenu(ToolbarFrame, varCellDimensions, cellSizeToDimensions(cellSize), 
                                  *dimensionOptions, command=resizeGrid, 
                                  style='design1.TMenubutton')
cellSizeSelector.grid(row=1, column=16, padx=5, pady=2, rowspan=2, sticky='w')

ttk.Label(ToolbarFrame, text="Dimensions", font=('Calibri', 9), background='lightgray').grid(
    row=3, column=16, pady=(0,2))


# ====================
# CANVAS SECTION
# ====================

CanvasFrame = tk.Frame(master=window, bg=Color_MazeBackground)
CanvasFrame.grid(row=1, column=0, sticky='nsew', padx=20, pady=(20, 10))

CanvasFrame.grid_rowconfigure(0, weight=1)
CanvasFrame.grid_columnconfigure(0, weight=1)

maze = tk.Canvas(master=CanvasFrame, height=mazeHeight, width=mazeWidth, bg=Color_NonSelectedCells, 
                 border=0, borderwidth=0, highlightbackground="black", highlightthickness=2)
maze.grid(row=0, column=0)


# ====================
# CORE FUNCTIONS
# ====================

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


def generateRandomMaze():
    """Generate a random maze using Prim's algorithm"""
    global selectedCell, numRow, numColumn, cellRectangles, lastCellRow, lastCellColumn
    global startPointX, startPointY, endPointX, endPointY
    
    # Clear everything first
    lastCellRow, lastCellColumn = -1, -1
    startPointX, startPointY, endPointX, endPointY = -1, -1, -1, -1
    selectedCell = [[0] * (numColumn + 1) for i in range(numRow + 1)]
    
    for a in range(numRow):
        selectedCell[a][numColumn] = 0
    for a in range(numColumn + 1):
        selectedCell[numRow][a] = 0
    
    maze.delete('all')
    cellRectangles.clear()
    
    spacing = 2
    
    start_offset_row = 1 if numRow % 2 == 0 else 0
    start_offset_col = 1 if numColumn % 2 == 0 else 0
    
    possible_rows = list(range(start_offset_row, numRow, spacing))
    possible_cols = list(range(start_offset_col, numColumn, spacing))
    
    if not possible_rows or not possible_cols:
        return
    
    start_row = random.choice(possible_rows)
    start_col = random.choice(possible_cols)
    
    selectedCell[start_row][start_col] = 1
    
    in_maze = {(start_row, start_col)}
    
    walls = []
    removed_walls = []
    
    for dr, dc in [(0, spacing), (0, -spacing), (spacing, 0), (-spacing, 0)]:
        wall_row = start_row + dr // 2
        wall_col = start_col + dc // 2
        new_row = start_row + dr
        new_col = start_col + dc
        
        if 0 <= new_row < numRow and 0 <= new_col < numColumn:
            walls.append((wall_row, wall_col, new_row, new_col))
    
    while walls:
        wall_row, wall_col, cell_row, cell_col = random.choice(walls)
        walls.remove((wall_row, wall_col, cell_row, cell_col))
        
        if (cell_row, cell_col) not in in_maze:
            selectedCell[wall_row][wall_col] = 1
            selectedCell[cell_row][cell_col] = 1
            in_maze.add((cell_row, cell_col))
            
            for dr, dc in [(0, spacing), (0, -spacing), (spacing, 0), (-spacing, 0)]:
                new_wall_row = cell_row + dr // 2
                new_wall_col = cell_col + dc // 2
                new_cell_row = cell_row + dr
                new_cell_col = cell_col + dc
                
                if 0 <= new_cell_row < numRow and 0 <= new_cell_col < numColumn:
                    if (new_cell_row, new_cell_col) not in in_maze:
                        wall_tuple = (new_wall_row, new_wall_col, new_cell_row, new_cell_col)
                        if wall_tuple not in walls:
                            walls.append(wall_tuple)
        else:
            removed_walls.append((wall_row, wall_col))
    
    loop_chance = 0.12
    for wall_row, wall_col in removed_walls:
        if random.random() < loop_chance:
            is_horizontal = False
            is_vertical = False
            
            if (0 <= wall_col - 1 < numColumn and 0 <= wall_col + 1 < numColumn and
                selectedCell[wall_row][wall_col - 1] == 1 and 
                selectedCell[wall_row][wall_col + 1] == 1):
                is_horizontal = True
            
            if (0 <= wall_row - 1 < numRow and 0 <= wall_row + 1 < numRow and
                selectedCell[wall_row - 1][wall_col] == 1 and 
                selectedCell[wall_row + 1][wall_col] == 1):
                is_vertical = True
            
            if is_horizontal or is_vertical:
                selectedCell[wall_row][wall_col] = 1
    
    # Redraw all cells
    for row in range(numRow):
        for column in range(numColumn):
            if selectedCell[row][column] == 1:
                xCell, yCell = column * cellSize, row * cellSize
                rect_id = maze.create_rectangle(xCell, yCell, xCell + cellSize, yCell + cellSize, 
                                              fill=Color_SelectedCells, outline='', tags='Cell')
                cellRectangles[(row, column)] = rect_id
    
    maze.tag_lower('Cell')
    drawGrid()
    drawLine()
    drawLine(optimizeMode=1)


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


# Parallel vertex detection helper
def detect_vertices_chunk(start_row, end_row, fast_calc_mode):
    """Detect vertices in a chunk of rows - runs in thread"""
    local_vertices = []
    local_dead = []
    
    for row in range(start_row, end_row):
        for column in range(0, numColumn):
            if selectedCell[row][column] == 1:
                if fast_calc_mode == 0:
                    # Outer Vertex
                    if selectedCell[row - 1][column] == 0 and selectedCell[row][column - 1] == 0 and selectedCell[row - 1][column - 1] == 0:
                        local_vertices.append([row, column])
                    if selectedCell[row - 1][column] == 0 and selectedCell[row][column + 1] == 0 and selectedCell[row - 1][column + 1] == 0:
                        local_vertices.append([row, column + 1])
                    if selectedCell[row + 1][column] == 0 and selectedCell[row][column - 1] == 0 and selectedCell[row + 1][column - 1] == 0:
                        local_vertices.append([row + 1, column])
                    if selectedCell[row + 1][column] == 0 and selectedCell[row][column + 1] == 0 and selectedCell[row + 1][column + 1] == 0:
                        local_vertices.append([row + 1, column + 1])
                    
                    # Inner Vertex
                    if selectedCell[row - 1][column] == 1 and selectedCell[row][column - 1] == 1 and selectedCell[row - 1][column - 1] == 0:
                        local_vertices.append([row, column])
                    if selectedCell[row - 1][column] == 1 and selectedCell[row][column + 1] == 1 and selectedCell[row - 1][column + 1] == 0:
                        local_vertices.append([row, column + 1])
                    if selectedCell[row + 1][column] == 1 and selectedCell[row][column - 1] == 1 and selectedCell[row + 1][column - 1] == 0:
                        local_vertices.append([row + 1, column])
                    if selectedCell[row + 1][column] == 1 and selectedCell[row][column + 1] == 1 and selectedCell[row + 1][column + 1] == 0:
                        local_vertices.append([row + 1, column + 1])
                else:
                    # Inner Vertex only
                    if selectedCell[row - 1][column] == 1 and selectedCell[row][column - 1] == 1 and selectedCell[row - 1][column - 1] == 0:
                        local_vertices.append([row, column])
                    if selectedCell[row - 1][column] == 1 and selectedCell[row][column + 1] == 1 and selectedCell[row - 1][column + 1] == 0:
                        local_vertices.append([row, column + 1])
                    if selectedCell[row + 1][column] == 1 and selectedCell[row][column - 1] == 1 and selectedCell[row + 1][column - 1] == 0:
                        local_vertices.append([row + 1, column])
                    if selectedCell[row + 1][column] == 1 and selectedCell[row][column + 1] == 1 and selectedCell[row + 1][column + 1] == 0:
                        local_vertices.append([row + 1, column + 1])
    
    # Detect dead vertices in this chunk
    for row in range(start_row, min(end_row + 1, numRow + 1)):
        for column in range(0, numColumn + 1):
            topLeft = selectedCell[row - 1][column - 1] if row > 0 and column > 0 else 0
            topRight = selectedCell[row - 1][column] if row > 0 and column <= numColumn else 0
            bottomLeft = selectedCell[row][column - 1] if row <= numRow and column > 0 else 0
            bottomRight = selectedCell[row][column] if row <= numRow and column <= numColumn else 0
            
            if topLeft == 1 and bottomRight == 1 and topRight == 0 and bottomLeft == 0:
                local_dead.append([row, column])
            elif topRight == 1 and bottomLeft == 1 and topLeft == 0 and bottomRight == 0:
                local_dead.append([row, column])
    
    return local_vertices, local_dead


def drawLine(optimizeMode=0):
    global mazeVertex, deadVertex, showPath, showVertex, showBorder, showSolution
    
    # Show border
    if showBorder.get() == 1 and optimizeMode == 0:
        drawLine_Border()
    elif showBorder.get() == 0:
        maze.delete('line_Border')
        numberEdge.configure(text='')
    
    # Show vertex - with parallelization
    if optimizeMode == 0:
        maze.delete('line_Vertex')
        
        # Split into chunks for parallel processing
        chunk_size = max(1, numRow // 4)
        futures = []
        fast_calc_mode = fastCalc.get()
        
        for i in range(0, numRow, chunk_size):
            end = min(i + chunk_size, numRow)
            future = executor.submit(detect_vertices_chunk, i, end, fast_calc_mode)
            futures.append(future)
        
        # Collect results
        all_vertices = []
        all_dead = []
        for future in futures:
            vertices, dead = future.result()
            all_vertices.extend(vertices)
            all_dead.extend(dead)
        
        mazeVertex = all_vertices
        deadVertex = all_dead
        
        if showVertex.get() == 1:
            for i in range(len(mazeVertex)):
                row, column = mazeVertex[i]
                maze.create_oval(column * cellSize - 3, row * cellSize - 3, 
                               column * cellSize + 3, row * cellSize + 3,
                               fill=Color_Line_Vertex, width=0, tags='line_Vertex')
            
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
    numberVertex.configure(text='Vertices: ' + str(len(mazeVertex)))
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
    numberEdge.configure(text='Edges: ' + str(countEdge + 1))


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


# Parallel path calculation helper
def calculate_paths_chunk(vertex_indices, maze_vertex_copy):
    """Calculate paths for a chunk of vertex pairs - runs in thread"""
    local_paths = []
    for i in vertex_indices:
        y0, x0 = maze_vertex_copy[i]
        for j in range(i + 1, len(maze_vertex_copy)):
            y1, x1 = maze_vertex_copy[j]
            if legitPath(x0, y0, x1, y1) == True:
                distance = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
                local_paths.append([i, j, distance, x0, y0, x1, y1])
    return local_paths


def drawLine_Path(optimizeMode=0):
    Timer_Solution = time.perf_counter()
    pathLength = 0
    
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
    
    # Line vertex - vertex with parallelization
    if optimizeMode == 0:
        mazePath = []
        vertex_count = len(mazeVertex)
        
        if vertex_count > 50:  # Only parallelize for larger graphs
            # Make a copy for thread safety
            maze_vertex_copy = mazeVertex.copy()
            
            # Split into chunks
            chunk_size = max(1, vertex_count // 4)
            futures = []
            
            for i in range(0, vertex_count, chunk_size):
                end = min(i + chunk_size, vertex_count)
                future = executor.submit(calculate_paths_chunk, list(range(i, end)), maze_vertex_copy)
                futures.append(future)
            
            # Collect results and draw on main thread
            for future in futures:
                paths = future.result()
                for i, j, distance, x0, y0, x1, y1 in paths:
                    if showPath.get() == 1:
                        maze.create_line(x0 * cellSize, y0 * cellSize, x1 * cellSize, y1 * cellSize,
                                       fill=Color_Line_Path, width=1, tags='line_Path')
                    countPath += 1
                    mazePath.append([i, j, distance])
        else:
            # Sequential for small graphs
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
    
    numberPath.configure(text='Paths: ' + str(countPath))
    
    if optimizeMode == 0:
        lastArchiveTimer_Path = time.perf_counter() - Timer_Solution
        timerProcessing_Path.configure(text='Visibility: ' + 
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
        
        timerProcessing_Solution.configure(text='Solution: ' + 
                                          str(round(Timer_Solution * 1000, 2)) + ' ms\n' +
                                          'Length: ' + str(round(pathLength / cellSize, 2)) + ' cells')


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
min_height = mazeHeight + 280
window.minsize(min_width, min_height)

# Cleanup on exit
def on_closing():
    executor.shutdown(wait=False)
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)

# Run
changeMode()
resizeGrid(cellSizeToDimensions(cellSize))
window.mainloop()
