import math
#prints 2d list in nice way (taken from 112 course notes)
def repr2dList(L):
    if (L == []): return '[]'
    output = [ ]
    rows = len(L)
    cols = max([len(L[row]) for row in range(rows)])
    M = [['']*cols for row in range(rows)]
    for row in range(rows):
        for col in range(len(L[row])):
            M[row][col] = repr(L[row][col])
    colWidths = [0] * cols
    for col in range(cols):
        colWidths[col] = max([len(M[row][col]) for row in range(rows)])
    output.append('[\n')
    for row in range(rows):
        output.append(' [ ')
        for col in range(cols):
            if (col > 0):
                output.append(', ' if col < len(L[row]) else '  ')
            output.append(M[row][col].rjust(colWidths[col]))
        output.append((' ],' if row < rows-1 else ' ]') + '\n')
    output.append(']')
    return ''.join(output)
def print2dList(L):
    print(repr2dList(L))
#converts potentially nested list to a tuple
def listToTuple(L):
    return tuple(listToTuple(val) if isinstance(val, list) else val for val in L)
#all component types are derived from component class
#nodes: list of points component is connected to
#flavor: type of component
class Component(object):
    def __init__(self, nodes, flavor):
        self.nodes = nodes
        self.flavor = flavor       
#subclass of Component
#voltage: voltage supplied by source (default 9V)
class DCVoltageSource(Component):
    def __init__(self, nodes, voltage):
        super().__init__(nodes, "DC Voltage Source")
        self.voltage = voltage
    def __repr__(self):
        return f'DC Voltage Source with a \nvoltage of {self.voltage} V at {self.nodes}'
    def __eq__(self, other):
        return (isinstance(other, DCVoltageSource) and self.nodes == other.nodes
            and self.voltage == other.voltage)
#subclass of Component
#resistance: resistance across resistor (default 100 ohms)
class Resistor(Component):
    def __init__(self, nodes, resistance):
        super().__init__(nodes, "Resistor")
        self.resistance = resistance
    def __repr__(self):
        return f'Resistor with a resistance \nof {self.resistance}ohms at {self.nodes}'
    def __eq__(self, other):
        return (isinstance(other, Resistor) and self.nodes == other.nodes
            and self.resistance == other.resistance)
#subclass of Component
class Wire(Component):
    def __init__(self, nodes):
        super().__init__(nodes, "Wire")
    def __repr__(self):
        return f'''Wire at {self.nodes}'''
    def __eq__(self, other):
        return (isinstance(other, Wire) and self.nodes == other.nodes)
#subclass of Component
#startnode == endNode (ground is attached at only 1 point)
class Ground(Component):
    def __init__(self, nodes):
        super().__init__(nodes, "Ground")
    def __repr__(self):
        return f'''Ground at {self.nodes}'''
    def __eq__(self, other):
        return (isinstance(other, Ground) and self.nodes == other.nodes)
#subclass of Component
#current: current supplied by source (default 1A)
class DCCurrentSource(Component):
    def __init__(self, nodes, current):
        super().__init__(nodes , "DC Current Source")
        self.current = current
    def __repr__(self):
        return f'''DC Current Source with a \ncurrent of {self.current} A at {self.nodes}'''
    def __eq__(self, other):
        return (isinstance(other, DCCurrentSource) and self.nodes == other.nodes
                and self.current == other.current)
#contains graph data structure and associated functions
#aList: adjacency list which contains neighbors to each node
#addNode: adds node to the dictionary (initially no neighbors)
#addEdge: adds connection between 2 nodes and assigns the type of connection
#getEdge: returns type of connection between 2 nodes
#getNeighbors: returns neighbors of a node
#findUniquePath: returns path between 2 nodes not already contained in solutions set
#uniquePathSolver: uses recursive backtracking to find unique path
#isUniqueSolution: determines if solution is unique
class Graph(object):
    def __init__(self):
        self.aList = {}
    def addNode(self, node):
        self.aList[node] = set()
    def addEdge(self, node0, node1, attributes):
        self.aList[node0].add((node1, attributes))
        self.aList[node1].add((node0, attributes))
    def getEdge(self, node0, node1):
        for neighbor in self.aList[node0]:
            if neighbor[0] == node1:
                return neighbor[1]
            else:
                return None
    def getNeighbors(self, node):
        return self.aList[node]
    def findUniquePath(self, startNode, endNode, solutions):
        pathSoFar = (startNode[0], startNode[1]),
        return self.uniquePathSolver(endNode, pathSoFar, solutions)
    def uniquePathSolver(self, endNode, pathSoFar, solutions):
        startNode = pathSoFar[-1]
        if startNode == endNode and self.isUniqueSolution(pathSoFar, solutions):
            return pathSoFar
        else:
            for neighbor in self.aList[startNode]:
                if tuple(neighbor[0]) not in pathSoFar:
                    pathSoFar += (neighbor[0][0], neighbor[0][1]),
                    solution = self.uniquePathSolver(endNode, pathSoFar, solutions)
                    if solution != None and self.isUniqueSolution(solution, solutions):
                        return solution
                    else:
                        pathSoFar = pathSoFar[:-1]
            return None
    def isUniqueSolution(self, solution, solutions):
        for sol in solutions:
            if solution[1] == sol[1]:
                return False
        return True
#contains conductance and solution matrices for associated netlist
#netlist: graph object containing all connected nodes in the netlist
#activeComponents: 2d list containing all component objects on the board
#netListCOmponents: 2d list containing only component objects in the netlist
#conductanceMatrix: square matrix with all conductances
#knownMatrix: 1x(n+m) matrix where n is nodes and m is voltage sources 
#and contains node currents and voltage source voltages
#nodeNums: maps each node to a node number in the matrix
#vNums: maps each component to a voltage source number in the matrix
#componentVals: dictionary of associated node voltages and component current
#setMatrices: initializes dimensions of matrix and adds appropriate resistances, voltages, and currents
#solveMatrices: uses gauss-jordan elimination to solve system of equations
#returns none if no legal solution exists
#knownMatrix now contains respective node voltages and voltage source currents
#isValidCircuit: determines if solution derived is legal
#setComponentVals: sets node voltages and component current for each component
class NodeMatrices(object):
    def __init__(self, netList, activeComponents):
        self.netList = netList
        self.activeComponents = activeComponents
        self.netListComponents = [[] for comType in self.activeComponents]
        self.conductanceMatrix = []
        self.knownMatrix = []
        self.nodeNums = {}
        self.vNums = {}
        self.componentVals = {}
    def setMatrices(self):
        addedIndices = set()
        count = 0
        for ground in self.activeComponents[3]:
            gNode = tuple(ground.nodes[0])
            if gNode in self.netList.aList:
                self.nodeNums[gNode] = -1
        for node in self.netList.aList:
            for neighbor in self.netList.aList[node]:
                index = neighbor[1]
                if index not in addedIndices:
                    self.netListComponents[index[0]].append(self.activeComponents[index[0]][index[1]])
                    addedIndices.add(index)
                if node not in self.nodeNums:
                    if index[0] == 3:
                        self.nodeNums[node] = -1
                    else:
                        self.nodeNums[node] = count
                        count += 1
        n = len(self.netList.aList) - len(self.netListComponents[3])
        m = len(self.netListComponents[0]) + len(self.netListComponents[1])
        print2dList(self.netListComponents)
        print(self.nodeNums)
        self.conductanceMatrix = [[0]*(n+m) for i in range(n+m)]
        self.knownMatrix = [[0] for i in range(n+m)]
        for comType in range(len(self.netListComponents)):
            if comType == 0:
                    for c in range(len(self.netListComponents[comType])):
                        com = self.netListComponents[comType][c]
                        nodeNum0 = self.nodeNums[tuple(com.nodes[0])]
                        nodeNum1 = self.nodeNums[tuple(com.nodes[1])]
                        self.vNums[(tuple(com.nodes[0]), tuple(com.nodes[1]))] = c
                        self.vNums[(tuple(com.nodes[1]), tuple(com.nodes[0]))] = c
                        if nodeNum0 == -1:
                            self.conductanceMatrix[nodeNum1][n + c] = 1
                            self.conductanceMatrix[n+c][nodeNum1] = 1
                        elif nodeNum1 == -1:
                            self.conductanceMatrix[nodeNum0][n + c] = -1
                            self.conductanceMatrix[n+c][nodeNum0] = -1
                        else:
                            self.conductanceMatrix[nodeNum1][n + c] = 1
                            self.conductanceMatrix[nodeNum0][n + c] = -1
                            self.conductanceMatrix[n+c][nodeNum1] = 1
                            self.conductanceMatrix[n+c][nodeNum0] = -1
            elif comType == 1:
                    for c in range(len(self.netListComponents[comType])):
                        com = self.netListComponents[comType][c]
                        nodeNum0 = self.nodeNums[tuple(com.nodes[0])]
                        nodeNum1 = self.nodeNums[tuple(com.nodes[1])]
                        vNum = n + len((self.netListComponents[0])) + c
                        self.vNums[(tuple(com.nodes[0]), tuple(com.nodes[1]))] = len((self.netListComponents[0])) + c
                        self.vNums[(tuple(com.nodes[1]), tuple(com.nodes[0]))] = len((self.netListComponents[0])) + c
                        if nodeNum0 == -1:
                            self.conductanceMatrix[nodeNum1][vNum] = 1
                            self.conductanceMatrix[vNum][nodeNum1] = 1
                        elif nodeNum1 == -1:
                            self.conductanceMatrix[nodeNum0][vNum] = -1
                            self.conductanceMatrix[vNum][nodeNum0] = -1
                        else:
                            self.conductanceMatrix[nodeNum1][vNum] = 1
                            self.conductanceMatrix[nodeNum0][vNum] = -1
                            self.conductanceMatrix[vNum][nodeNum1] = 1
                            self.conductanceMatrix[vNum][nodeNum0] = -1
                        self.knownMatrix[vNum] = [com.voltage]
                        print(self.knownMatrix[vNum])
            elif comType == 2:
                    for c in range(len(self.netListComponents[comType])):
                        com = self.netListComponents[comType][c] 
                        nodeNum0 = self.nodeNums[tuple(com.nodes[0])]
                        nodeNum1 = self.nodeNums[tuple(com.nodes[1])]
                        print(com, nodeNum0, nodeNum1)
                        if nodeNum0 == -1:
                            self.conductanceMatrix[nodeNum1][nodeNum1] += 1/com.resistance
                        elif nodeNum1 == -1:
                            self.conductanceMatrix[nodeNum0][nodeNum0] += 1/com.resistance
                        else:
                            self.conductanceMatrix[nodeNum0][nodeNum0] += 1/com.resistance
                            self.conductanceMatrix[nodeNum1][nodeNum1] += 1/com.resistance
                            self.conductanceMatrix[nodeNum0][nodeNum1] -= 1/com.resistance
                            self.conductanceMatrix[nodeNum1][nodeNum0] -= 1/com.resistance
            elif comType == 3:
                    pass
            elif comType == 4:
                    for c in range(len(self.netListComponents[comType])):
                        com = self.netListComponents[comType][c]
                        nodeNum0 = self.nodeNums[tuple(com.nodes[0])]
                        nodeNum1 = self.nodeNums[tuple(com.nodes[1])]
                        if nodeNum0 == -1:
                            self.knownMatrix[nodeNum1] = [-com.current]
                        elif nodeNum1 == -1:
                            self.knownMatrix[nodeNum0] = [com.current]
                        else:
                            self.knownMatrix[nodeNum0] = [com.current]
                            self.knownMatrix[nodeNum1] = [-com.current]
    def solveMatrices(self):
        print2dList(self.conductanceMatrix)
        print2dList(self.knownMatrix)
        for row in range(len(self.conductanceMatrix)):
            if  math.isclose(self.conductanceMatrix[row][row], 0, abs_tol = 1e-9):
                for newRow in range(row + 1, len(self.conductanceMatrix)):
                    if self.conductanceMatrix[newRow][row] != 0:
                        self.conductanceMatrix[row], self.conductanceMatrix[newRow] = self.conductanceMatrix[newRow], self.conductanceMatrix[row]
                        self.knownMatrix[row], self.knownMatrix[newRow] = self.knownMatrix[newRow], self.knownMatrix[row]
                        break
                if self.conductanceMatrix[row][row] == 0:
                    return None
            scale = self.conductanceMatrix[row][row]
            for col in range(len(self.conductanceMatrix[0])):
                self.conductanceMatrix[row][col] /= scale 
            self.knownMatrix[row][0] /= scale    
            for r2 in range(len(self.conductanceMatrix)):
                if r2 != row:
                    scale2 = self.conductanceMatrix[r2][row]
                    for col in range(len(self.conductanceMatrix[0])):
                        self.conductanceMatrix[r2][col] -=  (scale2)*(self.conductanceMatrix[row][col])    
                    self.knownMatrix[r2][0] -= (scale2)*(self.knownMatrix[row][0])
            print2dList(self.conductanceMatrix)
            print2dList(self.knownMatrix)
        if self.isValidCircuit():
            self.setComponentVals()
            return self.knownMatrix            
    def isValidCircuit(self):
        for node in self.netList.aList:
            nodeNum = self.nodeNums[node]
            if nodeNum == -1:
                nodeVoltage = 0
            else:
                nodeVoltage = self.knownMatrix[nodeNum][0]
            nodeCurrent = 0
            for neighbor in self.netList.aList[node]:
                node2 = neighbor[0]
                nodeNum2 = self.nodeNums[node2]
                if nodeNum2 == -1:
                    nodeVoltage2 = 0
                else:
                    nodeVoltage2 = self.knownMatrix[nodeNum2][0]
                index = neighbor[1]
                com = self.activeComponents[index[0]][index[1]]
                if index[0] == 0:
                    if not math.isclose(nodeVoltage, nodeVoltage2, abs_tol = 1e-5):
                        print("failed ground")
                        return False      
                    vNum = len(self.netList.aList) - len(self.netListComponents[3]) + self.vNums[(node, node2)]
                    if node == tuple(com.nodes[0]):                            
                        nodeCurrent -= self.knownMatrix[vNum][0]
                    else:
                        nodeCurrent += self.knownMatrix[vNum][0]
                elif index[0] == 1:
                    vNum = len(self.netList.aList) - len(self.netListComponents[3]) + self.vNums[(node, node2)]
                    if node == tuple(com.nodes[0]):  
                        if not math.isclose(nodeVoltage2 - nodeVoltage, com.voltage, rel_tol = 1e-5):
                            print("failed voltage source")
                            return False                          
                        nodeCurrent -= self.knownMatrix[vNum][0]
                    else:
                        if not math.isclose(nodeVoltage - nodeVoltage2, com.voltage, rel_tol = 1e-5):
                            print("failed voltage source")
                            return False 
                        nodeCurrent += self.knownMatrix[vNum][0]
                elif index[0] == 2:
                    nodeCurrent += (nodeVoltage - nodeVoltage2)/com.resistance
                elif index[0] == 3:
                    pass
                elif index[0] == 4:
                    if node == tuple(com.nodes[0]):                            
                        nodeCurrent -= com.current
                    else:
                        nodeCurrent += com.current
            print(node, nodeCurrent)
            if not math.isclose(nodeCurrent, 0, abs_tol = 1e-5):
                print("failed current")
                return False
        return True
    def setComponentVals(self):
        for comType in range(len(self.activeComponents)):
            for c in range(len(self.activeComponents[comType])):
                com = self.activeComponents[comType][c]
                if tuple(com.nodes[0]) in self.netList.aList and (tuple(com.nodes[1]), (comType, c)) in self.netList.aList[tuple(com.nodes[0])]:
                    nodeNum1 = self.nodeNums[tuple(com.nodes[0])]
                    nodeNum2 = self.nodeNums[tuple(com.nodes[1])]
                    if nodeNum1 == -1 and nodeNum2 == -1:
                        nodeVoltage1 = 0
                        nodeVoltage2 = 0
                    elif nodeNum1 == -1:
                        nodeVoltage1 = 0
                        nodeVoltage2 = self.knownMatrix[nodeNum2][0]   
                    elif nodeNum2 == -1:
                        nodeVoltage1 = self.knownMatrix[nodeNum1][0]   
                        nodeVoltage2 = 0
                    else:
                        nodeVoltage1 = self.knownMatrix[nodeNum1][0]                    
                        nodeVoltage2 = self.knownMatrix[nodeNum2][0]
                    print("gothere")
                    if comType == 0 or comType == 1:
                        vNum = len(self.netList.aList) - len(self.netListComponents[3]) + self.vNums[tuple(com.nodes[0]), tuple(com.nodes[1])]
                        comCurrent = -self.knownMatrix[vNum][0]
                    elif comType == 2:
                        comCurrent = abs(nodeVoltage1 - nodeVoltage2)/com.resistance
                    elif comType == 3:
                        comCurrent = 0
                    elif comType == 4:
                        comCurrent = com.current
                    self.componentVals[(comType, c)] = (nodeVoltage1, nodeVoltage2, comCurrent)
