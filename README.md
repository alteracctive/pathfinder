# Pathfinder


> A Python-based interactive maze designer and shortest path visualizer with advanced features.


**Pathfinder** is a GUI application built with Python and Tkinter that allows users to draw custom grid-based mazes, generate random mazes using Prim's algorithm, and immediately visualize the shortest path between two points using Dijkstra's algorithm. It serves as both a maze design tool and an educational visualization of graph theory concepts.


## Features


* **Interactive Maze Drawing:** Easily draw complex maze structures on a customizable grid with smooth Bresenham line drawing for continuous cell selection.
* **Random Maze Generation:** Generate perfect mazes with 1-cell thick walls using Prim's algorithm, with built-in loop creation for multiple solution paths.
* **Real-time Pathfinding:** Utilizes Dijkstra's algorithm to find the shortest path instantly as you modify the maze or move start/end points.
* **Grid Customization:** Adjust grid dimensions from 20×20 up to 90×30 cells to create simple coarse mazes or complex fine-grained labyrinths.
* **Advanced Vertex Detection:** 
    * **FastCalc Mode (Default):** Detects only inner vertices (corners where corridors meet) for optimal performance.
    * **Full Detection Mode:** Detects both inner and outer vertices for comprehensive analysis.
    * **Dead Vertex Detection:** Automatically identifies and marks invalid diagonal-only connections in dark purple.
* **Debug Visualizations:** Toggle various rendering layers to understand how the graph is constructed:
    * Show Grid Lines
    * Show Maze Borders
    * Show Vertices (nodes) - Regular vertices in magenta, dead vertices in dark purple
    * Show All Possible Paths (edges between vertices)
    * Show Shortest Path Solution
    * Mouse Trace (debug mode)
* **Performance Metrics:** View real-time statistics:
    * Number of vertices detected
    * Number of border edges
    * Number of valid paths between vertices
    * Visibility calculation time
    * Solution calculation time and path length
* **Optimized Rendering:** Efficient cell-by-cell updates with scheduled redrawing for smooth interaction even with complex mazes.


## Installation


### Prerequisites


* **Python 3.14+**
* **Tkinter:** This usually comes standard with Python installations on Windows.
    * *Note for Linux users:* You may need to install `python3-tk` separately (e.g., `sudo apt-get install python3-tk`).


### Setup


1.  Clone this repository:
    ```
    git clone https://github.com/alteracctive/Pathfinder.git
    cd Pathfinder
    ```
2.  Ensure you have the `icons` folder in the same directory as the main script, containing all necessary `.png` and `.ico` assets.
3.  Run the application:
    ```
    python main.py
    ```


## Usage Guide


The application interface features an organized toolbar at the top with clearly labeled sections and buttons with descriptive titles.


### 1. Main Modes


Select your working mode using the vertically stacked mode buttons:


* **Maze Mode:** The default mode for drawing walls and clearing paths.
* **Point Mode:** Used specifically for placing the Start (Green) and End (Red) points.


### 2. Tools Panel


**In Maze Mode:**
* **Select:** Left-click draws cells, right-click erases (default)
* **Unselect:** Left-click erases cells, right-click draws (inverted)
* **All:** Select all cells at once
* **Clear:** Unselect all cells at once
* **Generate (Random):** Create a random perfect maze with loops using Prim's algorithm


**In Point Mode:**
* **Start:** Set the starting point (green marker)
* **End:** Set the ending point (red marker)
* **Bigger/Smaller:** Adjust the size of point markers (1-9 pixels)


### 3. Controls & Mouse Interaction


| Mode | Left Mouse Button | Right Mouse Button |
| :--- | :--- | :--- |
| **Maze Mode (Select)** | Draw Cell (Wall) | Erase Cell (Path) |
| **Maze Mode (Unselect)** | Erase Cell (Path) | Draw Cell (Wall) |
| **Point Mode (Start)** | Set Start Point (Green) | Set End Point (Red) |
| **Point Mode (End)** | Set End Point (Red) | Set Start Point (Green) |


**Drawing Features:**
* Click and drag to draw/erase cells continuously
* Smooth line drawing with Bresenham's algorithm
* Real-time vertex and path updates


### 4. Display Options


Toggle various visualization layers:


* **Grid:** Shows/hides the base grid lines
* **Trace:** (Debug) Shows mouse cursor position and movement trail
* **Vertices:** Highlights the graph nodes
    * Regular vertices shown in magenta
    * Dead vertices (diagonal-only connections) shown in dark purple
* **Border:** Outlines the edges of maze walls
* **Paths:** Draws lines showing all valid connections between vertices
* **Solution:** Highlights the shortest path from Start to End in light slate blue
* **Quick (FastCalc):** Enables optimized vertex detection (inner vertices only) - **ON by default**


### 5. Grid Customization


Use the **Grid** dropdown to select from preset dimensions:
* 90×45 (20px cells)
* 72×36 (25px cells)
* 60×30 (30px cells)
* 50×25 (36px cells) - Default
* 40×20 (45px cells)
* 36×18 (50px cells)
* 30×15 (60px cells)


### 6. Statistics Panel


Real-time information display:
* **Vertices:** Number of detected graph nodes
* **Edges:** Number of maze border segments
* **Paths:** Number of valid connections between vertices
* **Visibility Time:** Time taken to calculate visible paths (in milliseconds)
* **Solution Time:** Time taken to compute shortest path
* **Solution Length:** Length of shortest path in cell units


## Key Improvements

* **Enhanced UI:** Clean, organized toolbar with section headers and button titles
* **Random Maze Generation:** One-click generation of perfect mazes with configurable loops
* **Dead Vertex Detection:** Prevents invalid pathfinding through diagonal-only connections
* **Real-time Path Updates:** Paths automatically recalculate when moving start/end points
* **Performance Optimized:** FastCalc mode reduces vertex detection overhead by 50%+
* **Multi Threading:** Use multi threading to improve calculation performance (Tkinter is not thread-safe)



## Algorithm Details


**Maze Generation:** Uses Prim's algorithm to create perfect mazes with 1-cell thick walls. A configurable percentage (~12%) of rejected walls are removed to create loops and multiple solution paths.


**Pathfinding:** Implements Dijkstra's algorithm with dead vertex avoidance. The graph is constructed using detected vertices as nodes and line-of-sight paths as weighted edges.


**Vertex Detection:** 
* **FastCalc Mode:** Detects inner vertices only (where two corridors meet at a diagonal empty cell)
* **Full Mode:** Detects both inner and outer vertices (all corners of the maze structure)


## Performance
* Efficient cell rendering using dictionary-based rectangle tracking
* Scheduled redrawing during drag operations (50ms batching)
* FastCalc mode significantly improves performance on large mazes
* Average solution time: <10ms for typical mazes


## Known Limitations
* Very large mazes (>100×50 cells) may experience slower path calculation with FastCalc disabled
* Mouse trace debug mode may impact performance when enabled

## Author


**Alteracctive** - [GitHub](https://github.com/alteracctive)

