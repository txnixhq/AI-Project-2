import random
from collections import deque
import pdb



class Cell:
    def __init__(self):
        self.isClosed= True
        self.hasBot= False
        self.hasFire= False
        self.hasButton = False 
        self.neighbors= []
    

class Ship:
    def __init__(self, D, flammability):
        self.D = D
        self.flammability= flammability
        self.grid= self.createGrid(D)
        self.botPosition = None
        self.initFire = None
        self.buttonPos = None
        self.openRandom()
        self.openCells()
        self.openRandomClosedNeighbors()
        self.placeBot()
        self.placeFire()
        self.placeButton()
        self.failed= False
        self.success= False
                   

    #creating the 2D grid
    def createGrid(self, D):
        grid = [[Cell() for _ in range(D)] for _ in range(D)]

        for i in range(D):
            for j in range(D):
                if i > 0:
                    grid[i][j].neighbors.append(grid[i - 1][j])
                if i < D - 1:
                    grid[i][j].neighbors.append(grid[i + 1][j])
                if j > 0:
                    grid[i][j].neighbors.append(grid[i][j - 1])
                if j < D - 1:
                    grid[i][j].neighbors.append(grid[i][j + 1])
    
        return grid

    #randomly opens a square/cell inside
    def openRandom(self):
        size = self.D
        border_size = 2  #width of the border excludess exterior
        rRow= random.randint(border_size, size - border_size - 1)
        rCol = random.randint(border_size, size - border_size - 1)
        self.grid[rRow][rCol].isClosed = False

    def openCells(self):
        while True:
            closedCells = []

            for i in range(1, self.D-1):
                for j in range(1, self.D-1):
                    if self.grid[i][j].isClosed:
                        openNeighbors = 0
                        for n in self.grid[i][j].neighbors:
                            if not n.isClosed:
                                openNeighbors += 1
                        if openNeighbors== 1:
                            closedCells.append((i, j))

            if not closedCells:
                break
            

            randomCell = random.choice(closedCells)
            self.grid[randomCell[0]][randomCell[1]].isClosed = False

    def findDeadEnds(self):
            deadEnds = []

            for i in range(1, self.D-1):
                for j in range(1, self.D-1):
                    if not self.grid[i][j].isClosed:
                        openNeighbors = 0
                        for n in self.grid[i][j].neighbors:
                            if not n.isClosed:
                                openNeighbors += 1
                        if openNeighbors== 1:
                            deadEnds.append((i, j))

            return deadEnds


    def openRandomClosedNeighbors(self):
        deadEnds = self.findDeadEnds()

        num = len(deadEnds) // 2 #half of deadends deleted
        for _ in range(num):
            if deadEnds:
                i, j = random.choice(deadEnds)
                neighbors = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
                clNeighbors = [(x, y) for x, y in neighbors if 0 < x < self.D-1 and 0 < y < self.D-1 and self.grid[x][y].isClosed]
                if clNeighbors:
                    randNeighbor = random.choice(clNeighbors)
                    self.grid[randNeighbor[0]][randNeighbor[1]].isClosed = False
                    deadEnds.remove((i, j))  #remove orig dead end cell



    def placeBot(self):
        open_cells = [(i, j) for i in range(self.D) for j in range(self.D) if not self.grid[i][j].isClosed]
        if open_cells:
            i, j = random.choice(open_cells)
            self.grid[i][j].hasBot = True
            self.botPosition = (i, j)

    def placeFire(self):
        open_cells = [(i, j) for i in range(self.D) for j in range(self.D) if not self.grid[i][j].isClosed]
        if open_cells:
            i, j = random.choice(open_cells)
            self.grid[i][j].hasFire = True
            self.initFire = (i, j)

    def placeButton(self):
        open_cells = [(i, j) for i in range(self.D) for j in range(self.D) if not self.grid[i][j].isClosed]
        if open_cells:
            i, j = random.choice(open_cells)
            self.grid[i][j].hasButton = True
            self.buttonPos = (i, j)

    #spread fire every step from initial fire
    def spreadFire(self):

        new_fire_cells = []

        for i in range(self.D):
            for j in range(self.D):
                if not self.grid[i][j].isClosed:
                    burning_neighbors = 0
                    for neighbor in self.grid[i][j].neighbors:
                        if neighbor.hasFire:
                            burning_neighbors += 1
                        
                    if not self.grid[i][j].hasFire:
                        probability = 1 - (1 - self.flammability) ** burning_neighbors
                        if random.random()<probability:
                            new_fire_cells.append((i, j))

        #update the cells to be on fire
        for i, j in new_fire_cells:
            self.grid[i][j].hasFire = True


                            
    # updates or moves the bot in the ship according to the path          
    def updateBotPosition(self, new_position):
        #clear the bot curr position
        i, j = self.botPosition
        self.grid[i][j].hasBot = False

        # Update the bot's position to the new cell
        self.botPosition = new_position
        i, j = new_position
        self.grid[i][j].hasBot = True

    #utilize different algorithms to find the shortest path
    def calculateShortestPath(self, botNo):
        
        if botNo == 1:
            #initialize queue for BFS
            queue = [(self.botPosition, [])]
            
            visited = set()

            while queue:
                current, path = queue.pop(0)
                row, col = current

                

                if self.grid[row][col].hasButton:
                    # found button, return path
                    return path
                
                

                for neighbor in self.grid[row][col].neighbors:
                    neighbor_row, neighbor_col = None, None
                    for i in range(self.D):
                        for j in range(self.D):
                            if self.grid[i][j] == neighbor:
                                neighbor_row, neighbor_col = i, j
                                break

                    #Skip if neighbor is same or the closed or the init fire or visited
                    if (neighbor_row, neighbor_col) == self.botPosition or \
                        self.grid[neighbor_row][neighbor_col].isClosed or \
                        (neighbor_row, neighbor_col) == self.initFire or \
                        (neighbor_row, neighbor_col) in visited:
                        continue

                    #add the neighbor to visited set
                    visited.add((neighbor_row, neighbor_col))
                    #add the neighbor to queue with the updated path
                    queue.append(((neighbor_row, neighbor_col), path + [(neighbor_row, neighbor_col)]))

            # If no valid path is found return an empty path
            return []
        
        #bot 2
        elif botNo == 2:
            queue = [(self.botPosition, [])]

            visited = set()

            while queue:
                current, path = queue.pop(0)
                row, col = current

                if self.grid[row][col].hasButton:
                    return path
                
                

                for neighbor in self.grid[row][col].neighbors:
                    neighbor_row, neighbor_col = None, None
                    for i in range(self.D):
                        for j in range(self.D):
                            if self.grid[i][j] == neighbor:
                                neighbor_row, neighbor_col = i, j
                                break

                    # Skip if neighbor is same or the closed or fire or visited
                    if (neighbor_row, neighbor_col) == self.botPosition or \
                        self.grid[neighbor_row][neighbor_col].isClosed or \
                        self.grid[neighbor_row][neighbor_col].hasFire or \
                        (neighbor_row, neighbor_col) in visited:
                        continue

                    # Add the neighbor to the visited set
                    visited.add((neighbor_row, neighbor_col))
                    # Add the neighbor to the queue with the updated path
                    queue.append(((neighbor_row, neighbor_col), path + [(neighbor_row, neighbor_col)]))

            # If no valid path is found, return an empty path
            return []
        
        #bot 3
        elif botNo== 3:
            # Define a set to store the cells to avoid
            cells_to_avoid = set()

            # Add the current fire cells and their adjacent cells to the set of cells to avoid
            for i in range(self.D):
                for j in range(self.D):
                    if self.grid[i][j].hasFire:
                        cells_to_avoid.add((i, j))
                    if self.grid[i][j].isClosed:
                        cells_to_avoid.add((i, j))

            queue = [(self.botPosition, [])]

            visited = set()

            while queue:
                current, path = queue.pop(0)
                row, col = current

                if self.grid[row][col].hasButton:
                    return path
                
                

                for neighbor in self.grid[row][col].neighbors:
                    neighbor_row, neighbor_col = None, None
                    for i in range(self.D):
                        for j in range(self.D):
                            if self.grid[i][j] == neighbor:
                                neighbor_row, neighbor_col = i, j
                                break

                    # Skip if neighbor is same or the closed or fire or visited
                    if (neighbor_row, neighbor_col) == self.botPosition or \
                        self.grid[neighbor_row][neighbor_col].isClosed or \
                        (neighbor_row, neighbor_col) in cells_to_avoid or \
                        (neighbor_row, neighbor_col) in visited:
                        continue

                    # Add the neighbor to the visited set
                    visited.add((neighbor_row, neighbor_col))
                    # Add the neighbor to the queue with the updated path
                    queue.append(((neighbor_row, neighbor_col), path + [(neighbor_row, neighbor_col)]))

            # If no valid path is found, return an empty path
            return []


        #this is bot 4: uses A*, dynamic planning and adaptive heuristic
        elif botNo== 4:
            #define a set to store the cells to avoid
            cells_to_avoid = set()
            nearest_fire = None
            nearest_fire_dist = float('inf')

            #add the current fire cells and their adjacent cells to the set of cells to avoid
            for i in range(self.D):
                for j in range(self.D):
                    if self.grid[i][j].hasFire:
                        cells_to_avoid.add((i, j))
                        # Calculate distance to the nearest fire cell
                        fire_dist= abs(i - self.botPosition[0])+ abs(j - self.botPosition[1])
                        if fire_dist < nearest_fire_dist:
                            nearest_fire_dist = fire_dist
                            nearest_fire = (i, j)

                    if self.grid[i][j].isClosed:
                        cells_to_avoid.add((i, j))

            # Initialize A* search with a priority queue
            pQueue = [(0, self.botPosition, [])]  # (f-score, current cell, path)
            closedSet = set()

            while pQueue:
                _, current, path = min(pQueue)  # Get the cell with the lowest f-score
                pQueue.remove((_, current, path))
                closedSet.add(current)
                row, col = current

                if self.grid[row][col].hasButton:
                    # Found the button, return the path
                    return path

                for neighbor in self.grid[row][col].neighbors:
                    neighbor_row, neighbor_col = None, None
                    for i in range(self.D):
                        for j in range(self.D):
                            if self.grid[i][j] == neighbor:
                                neighbor_row, neighbor_col = i, j
                                break

                    if (neighbor_row, neighbor_col) == self.botPosition or \
                        self.grid[neighbor_row][neighbor_col].isClosed or \
                        (neighbor_row, neighbor_col) in cells_to_avoid or \
                        (neighbor_row, neighbor_col) in closedSet:
                        continue

                    l = len(path)  # The cost of the path so far
                    h = abs(neighbor_row - self.buttonPos[0]) + abs(neighbor_col - self.buttonPos[1])  # Manhattan distance heuristic
                    # Add the adaptive heuristic (weight it based on the nearest fire cell)
                    if nearest_fire_dist > 0:
                        h += 1 /(nearest_fire_dist)
                    f = l + h

                    if (f, (neighbor_row, neighbor_col), path + [(neighbor_row, neighbor_col)]) not in pQueue:
                        pQueue.append((f, (neighbor_row, neighbor_col), path + [(neighbor_row, neighbor_col)]))

            # If no valid path is found, return an empty path
            return []

    #main method to execute the tasks in order
    def task(self, botNo):
        if botNo == 1:
        
            path = self.calculateShortestPath(botNo)

            if not path:
                return "no path - FAIL"

            while path:

                self.printGrid()
                print("//////////////////////")

                # Pick the first cell from the path and update the bot's position
                next_cell = path.pop(0)
                self.updateBotPosition(next_cell)

                if self.grid[self.botPosition[0]][self.botPosition[1]].hasButton:
                    return "SUCCESS"
                
                self.spreadFire()
                

                if self.grid[self.botPosition[0]][self.botPosition[1]].hasFire or \
                    self.grid[self.buttonPos[0]][self.buttonPos[1]].hasFire:
                        return "FAIL"
                    
                


            return "FAIL"
        
        else:
        


            while not self.failed and not self.success:
                # Attempt to find a path to the button
                path = self.calculateShortestPath(botNo)
                #print(path)

                self.printGrid()
                print("//////////////////////")
                
                if not path:
                    # If no path is found, try to find a path based only on current fire cells
                    path = self.calculateShortestPath(2)
           
                    if path:
                        next_cell = path[0]
                        self.updateBotPosition(next_cell)
                    elif not path:
                        # Handle the case when neither path is found
                        self.failed = True
                        return "no path - FAIL"

                if path:
                    # If a valid path is found, move the bot
                    next_cell = path[0]
                    self.updateBotPosition(next_cell)



                if self.botPosition == self.buttonPos:
                    self.success = True
                    return "SUCCESS"

                self.spreadFire()

                if self.grid[self.botPosition[0]][self.botPosition[1]].hasFire or \
                    self.grid[self.buttonPos[0]][self.buttonPos[1]].hasFire:
                    self.failed = True
                    return "FAIL"

 

    #visual representation of the grid        
    def printGrid(self):
        for row in self.grid:
                rowStr = ""
                for cell in row:
                    if cell.isClosed:
                        rowStr += "X "
                    else:
                        if cell.hasBot:
                            rowStr += "\033[92m* \033[0m" #green
                        elif cell.hasButton:
                            rowStr += "\033[94m* \033[0m" #blue
                        elif cell.hasFire:
                            rowStr += "\033[91m* \033[0m" #red
                        else:
                            rowStr += "  "
                print(rowStr)



if __name__ == "__main__":
    D = int(input("Enter ship size: "))
    flammability = float(input("Enter Flammability(q) of the ship (between 0 and 1): "))
    ship = Ship(D, flammability)

    botNo = int(input("Choose bot (1, 2, 3, or 4): "))
    result = ship.task(botNo)
    ship.printGrid()
    print(result)
    if result == "SUCCESS":
        print("Mission Successful!")
    else:
        print("Mission Failed")


