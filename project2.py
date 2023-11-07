import random
from collections import deque
import pdb



class Cell:
    def __init__(self):
        self.isClosed= True
        self.hasBot= False
        self.hasLeak = False
        self.neighbors= []
    

class Ship:
    def __init__(self, D, detectionRange):
        self.D = D
        self.grid= self.createGrid(D)
        self.detectionRange = detectionRange
        self.botPosition = None
        self.detectionSQ= []
        self.openRandom()
        self.openCells()
        self.openRandomClosedNeighbors()
        self.placeBot()
        self.placeLeak()
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

    def placeLeak(self):
        bot_x, bot_y = self.botPosition

        # Calculate the detection square boundaries
        detection_min_x = bot_x - self.detectionRange
        detection_max_x = bot_x + self.detectionRange
        detection_min_y = bot_y - self.detectionRange
        detection_max_y = bot_y + self.detectionRange

        # Create a list of open cells outside the detection square
        outside_detection_square = [(i, j) for i in range(self.D) for j in range(self.D)
                                    if not self.grid[i][j].isClosed and
                                    (i < detection_min_x or i > detection_max_x or
                                    j < detection_min_y or j > detection_max_y)]

        if outside_detection_square:
            i, j = random.choice(outside_detection_square)
            self.grid[i][j].hasLeak = True

        # Store the coordinates of the detection square
        self.detection_square = [(detection_min_x, detection_max_x, detection_min_y, detection_max_y)]



                            
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
        
        pass

    #main method to execute the tasks in order
    def task(self):
        pass
 

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
                        elif cell.hasLeak:
                            rowStr += "\033[94m* \033[0m" #blue
                        else:
                            rowStr += "  "
                print(rowStr)



if __name__ == "__main__":
    D = 50
    ship = Ship(D, 2)


    #result = ship.task()
    ship.printGrid()

    for square in ship.detection_square:
            print(f"Detection Square Coordinates: {square}")
    """print(result)
    if result == "SUCCESS":
        print("Mission Successful!")
    else:
        print("Mission Failed")
        """


