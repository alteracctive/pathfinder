# Pathseeker

> A Python-based interactive maze designer and shortest path visualizer.

**Pathseeker** is a GUI application built with Python and Tkinter that allows users to draw custom grid-based mazes and immediately visualize the shortest path between two points using Dijkstra's algorithm. It serves as both a maze design tool and an educational visualization of graph theory concepts.

## ✨ Features

* **Interactive Maze Drawing:** Easily draw complex maze structures on a customizable grid.
* **Real-time Pathfinding:** Utilizes Dijkstra's algorithm to find the shortest path instantly as you modify the maze.
* **Grid Customization:** Adjust cell sizes to create simple coarse mazes or complex fine-grained labyrinths.
* **Debug Visualizations:** Toggle various rendering layers to understand how the graph is constructed:
    * Show Grid
    * Show Maze Borders
    * Show Vertices (nodes)
    * Show All Possible Paths (edges)
    * Show Solution
* **Performance Metrics:** View real-time statistics on the number of vertices, edges, and calculation times.
* **Pattern Tool:** Quickly stamp predefined patterns into your maze.

## 🛠️ Installation

### Prerequisites

* **Python 3.10**
* **Tkinter with Tix:** This usually comes standard with Python 3.10 installations on Windows.
    * *Note for Linux users:* You may need to install `python3-tk` and `tix` separately (e.g., `sudo apt-get install python3-tk python3-tix`).

### Setup

1.  Clone this repository:
    ```bash
    git clone https://github.com/alteracctive/pathfinder.git
    cd pathfinder
    ```
2.  Ensure you have the `icons` folder in the same directory as the main script, containing all necessary `.png` and `.ico` assets.
3.  Run the application:
    ```bash
    python main.py
    ```

## 🎮 Usage Guide

The application interface is divided into three main sections: **Modes**, **Tools**, and **Debug/Options**.

### 1. Main Modes (Left Panel)

* **Maze Mode:** The default mode for drawing walls and clearing paths.
* **Point Mode:** Used specifically for placing the Start (Green) and End (Red) points.

### 2. Controls & Mouse Interaction

| Mode | Left Mouse Button | Right Mouse Button |
| :--- | :--- | :--- |
| **Maze Mode** | Select/Draw Cell (Wall) | Unselect/Clear Cell (Path) |
| **Point Mode** | Set Start Point (Green) | Set End Point (Red) |

*(Note: You can invert these default mouse behaviors using the toggle buttons in the Tools panel)*

### 3. Visualization & Debug (Right Panel)

Use the checkboxes on the top right to visualize how the program interprets your maze:

* **Grid:** Toggles the base grid lines.
* **Mouse Trace:** (Debug) Shows exactly where the mouse input is being registered.
* **Vertex:** Highlights the "nodes" of the graph. Nodes are automatically generated at corners and intersections.
* **Border:** Outlines the edges of selected wall cells.
* **Path:** Draws lines representing all valid connections (edges) between vertices.
* **Solution:** Highlights the shortest path from Start to End.
* **FastCalc:** Toggles an optimized calculation mode for complex grids.