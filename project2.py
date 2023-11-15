import random
import math
from collections import deque
import heapq
import pdb



class Cell:
    def __init__(self):
        self.isClosed= True
        self.hasBot= False
        self.hasLeak = False
        self.neighbors= []
    

class Ship:
    def __init__(self, D, detectionRange, alpha):
        self.D = D
        self.grid= self.createGrid(D)
        self.detectionRange = detectionRange
        self.alpha = alpha
        self.botPosition = None
        self.detectionSQ= []
        self.openRandom()
        self.openCells()
        self.openRandomClosedNeighbors()
        self.placeBot()
        self.placeLeak()
                   

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
    def calculateShortestPathOld(self, botNo):
        pass

    #main method to execute the tasks in order
    def task(self):
        pass

    def distance(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) + abs(y1 - y2)


    def updateDetectionSquare(self):
        bot_x, bot_y = self.botPosition
        detection_min_x = max(bot_x - self.detectionRange, 0)
        detection_max_x = min(bot_x + self.detectionRange, self.D - 1)
        detection_min_y = max(bot_y - self.detectionRange, 0)
        detection_max_y = min(bot_y + self.detectionRange, self.D - 1)
        self.detectionSQ = [(i, j) for i in range(detection_min_x, detection_max_x + 1)
                                for j in range(detection_min_y, detection_max_y + 1)]
        
    
    def runDetectionSquare(self):
        for i, j in self.detectionSQ:
            if self.grid[i][j].hasLeak:
                return True
        return False

    def bot1(self):
        MAY_CONTAIN_LEAK = [(i, j) for i in range(self.D) for j in range(self.D)
                            if not self.grid[i][j].isClosed and not self.grid[i][j].hasBot]

        visited_cells = set()  # Keep track of visited cells
        total_actions = 0

        while not self.grid[self.botPosition[0]][self.botPosition[1]].hasLeak:
            self.updateDetectionSquare()

            total_actions +=1
            if self.runDetectionSquare():
                MAY_CONTAIN_LEAK = list(set(MAY_CONTAIN_LEAK).intersection(self.detectionSQ))
                print("check")
            else:
                MAY_CONTAIN_LEAK = list(set(MAY_CONTAIN_LEAK).difference(self.detectionSQ))
                print("check2")

            next_locations = []

            if MAY_CONTAIN_LEAK:
                min_distance = float('inf')

                for location in MAY_CONTAIN_LEAK:
                    dist = self.distance(self.botPosition, location)
                    if dist < min_distance:
                        if location not in visited_cells:  # Check if the location has not been visited
                            min_distance = dist
                            next_locations = [location]
                    elif dist == min_distance and location not in visited_cells:
                        next_locations.append(location)

                if next_locations:
                    print("yes")
                    next_location = random.choice(next_locations)
                    total_actions += self.distance(self.botPosition, next_location)
                    self.updateBotPosition(next_location)
                    visited_cells.add(next_location)  # Mark the next location as visited
                else:
                    total_actions = -1  # No available next locations
                    break

        return total_actions

    def bot2(self):
        MAY_CONTAIN_LEAK = [(i, j) for i in range(self.D) for j in range(self.D)
                            if not self.grid[i][j].isClosed and not self.grid[i][j].hasBot]

        visited_cells = set()
        total_actions = 0

        while not self.grid[self.botPosition[0]][self.botPosition[1]].hasLeak:
            self.updateDetectionSquare()

            if self.runDetectionSquare():
                MAY_CONTAIN_LEAK = list(set(MAY_CONTAIN_LEAK).intersection(self.detectionSQ))
                print("Leak detected!")

                # Create the shortest path to the leak location
                shortest_path = self.calculateShortestPathBFS(self.botPosition)

                if shortest_path:
                    # Move along the shortest path
                    for next_location in shortest_path:
                        total_actions += 1
                        self.updateBotPosition(next_location)
                        visited_cells.add(next_location)

                    # Clear MAY_CONTAIN_LEAK since the leak has been found
                    MAY_CONTAIN_LEAK = []
                else:
                    print("Error: Shortest path not found.")
                    total_actions = -1
                    break

            else:
                MAY_CONTAIN_LEAK = list(set(MAY_CONTAIN_LEAK).difference(self.detectionSQ))

            next_locations = []

            if MAY_CONTAIN_LEAK:
                min_distance = float('inf')

                for location in MAY_CONTAIN_LEAK:
                    dist = self.distance(self.botPosition, location)
                    if dist < min_distance:
                        if location not in visited_cells:
                            min_distance = dist
                            next_locations = [location]
                    elif dist == min_distance and location not in visited_cells:
                        next_locations.append(location)

                if next_locations:
                    next_location = random.choice(next_locations)
                    total_actions += self.distance(self.botPosition, next_location)
                    self.updateBotPosition(next_location)
                    visited_cells.add(next_location)
                else:
                    total_actions = -1  # No available next locations
                    break

        return total_actions


    def calculateShortestPathBFS(self, start):
        # Initialize queue for BFS
        queue = [(start, [])]
        visited = set()

        while queue:
            current, path = queue.pop(0)
            row, col = current

            # Check if the current cell has a leak
            if self.grid[row][col].hasLeak:
                return path  # Found leak, return path

            # Iterate over neighbors
            for neighbor in self.grid[row][col].neighbors:
                neighbor_row, neighbor_col = None, None
                for i in range(self.D):
                    for j in range(self.D):
                        if self.grid[i][j] == neighbor:
                            neighbor_row, neighbor_col = i, j
                            break

                # Skip if neighbor is closed or visited
                if self.grid[neighbor_row][neighbor_col].isClosed or (neighbor_row, neighbor_col) in visited:
                    continue

                # Add the neighbor to the visited set
                visited.add((neighbor_row, neighbor_col))

                # Add the neighbor to the queue with the updated path
                queue.append(((neighbor_row, neighbor_col), path + [(neighbor_row, neighbor_col)]))

        # If no valid path to a leak is found, return an empty path
        return []

    def path_from_to(self, start, end):
        if start == end:
            return [end]

        queue = deque([(start, [])])
        visited = set([start])

        while queue:
            current, path = queue.popleft()
            if current == end:
                return path + [end]

            for neighbor in self.grid[current[0]][current[1]].neighbors:
                neighbor_position = (self.get_cell_position(neighbor))
                if neighbor_position not in visited and not neighbor.isClosed:
                    visited.add(neighbor_position)
                    queue.append((neighbor_position, path + [current]))

        return []  # No path found

    def get_cell_position(self, cell):
        for i in range(self.D):
            for j in range(self.D):
                if self.grid[i][j] == cell:
                    return (i, j)
        return None




    def initialize_probability_matrix(self):
        open_cells = [(i, j) for i in range(self.D) for j in range(self.D) if not self.grid[i][j].isClosed]
        num_open_cells = len(open_cells)
        return {cell: 1.0 / num_open_cells for cell in open_cells}

    def beep_probability(self, distance):
        return math.exp(-self.alpha * (distance - 1))

    def bot_enters_cell_probability_update(self, probability_matrix, bot_location):
        for cell in probability_matrix:
            if cell != bot_location and probability_matrix[bot_location] != 1:
                probability_matrix[cell] += probability_matrix[bot_location] / (1-probability_matrix[bot_location]) #(len(probability_matrix) - 1)
        probability_matrix[bot_location] = 0
        return probability_matrix

    def beep_probability_update(self, probability_matrix, bot_location):
        for cell in probability_matrix:
            distance = self.distance(bot_location, cell)
            probability_matrix[cell] *= self.beep_probability(distance)
        total_prob = sum(probability_matrix.values())
        for cell in probability_matrix:
            probability_matrix[cell] /= total_prob
        return probability_matrix

    def no_beep_probability_update(self, probability_matrix, bot_location):
        for cell in probability_matrix:
            distance = self.distance(bot_location, cell)
            probability_matrix[cell] *= (1 - self.beep_probability(distance))
        total_prob = sum(probability_matrix.values())
        for cell in probability_matrix:
            probability_matrix[cell] /= total_prob
        return probability_matrix

    def get_location_of_max_probability(self, probability_matrix):
        return max(probability_matrix, key=probability_matrix.get)

    def bot3(self):
        probability_matrix = self.initialize_probability_matrix()
        total_actions = 0
        visited_cells = set()  # Keep track of visited cells

        while not self.grid[self.botPosition[0]][self.botPosition[1]].hasLeak:
            self.printGrid()
            print(total_actions)
            visited_cells.add(self.botPosition)
            probability_matrix = self.bot_enters_cell_probability_update(probability_matrix, self.botPosition)

            # Simulate beep detection
            beep_detected = random.random() <= self.beep_probability(1)  # Max probability when on the leak
            total_actions += 1

            if beep_detected:
                probability_matrix = self.beep_probability_update(probability_matrix, self.botPosition)
            else:
                probability_matrix = self.no_beep_probability_update(probability_matrix, self.botPosition)

            # Reduce the probability of revisiting cells
            for cell in visited_cells:
                probability_matrix[cell] = 0

            # Find the next location with the highest probability
            next_location = self.get_location_of_max_probability(probability_matrix)
            d = self.distance(self.botPosition, next_location)

            # Move to the next location
            self.updateBotPosition(next_location)
            total_actions += d

            # If the bot has found the leak, end the loop
            if self.grid[next_location[0]][next_location[1]].hasLeak:
                break

        return total_actions





    #visual representation of the grid        
    def printGrid(self):
        for row in ship.grid:
                rowStr = ""
                for cell in row:
                    if cell.isClosed:
                        rowStr += "X "
                    else:
                        if cell.hasBot and cell.hasLeak:
                            rowStr += "\033[93m* \033[0m" #yellow
                        elif cell.hasBot:
                            rowStr += "\033[92m* \033[0m" #green
                        elif cell.hasLeak:
                            rowStr += "\033[94m* \033[0m" #blue
                        else:
                            rowStr += "  "
                print(rowStr)



if __name__ == "__main__":
    D = 30
    alpha = 0.3
    ship = Ship(D, 10, alpha)


    bot = 3  # Choose the bot number here
    if bot == 1:
        total_actions = ship.bot1()
    elif bot == 2:
        total_actions = ship.bot2()
    elif bot == 3:
        total_actions = ship.bot3()  # Run bot3

    print(f"Total actions for Bot {bot}: {total_actions}")
    ship.printGrid()



"""
our bot 3 is taking more actions- action is 1 for detect and distance for move
bot 7- which is two leaks. how to change/ update the probabilities.


"""
