from cmu_112_graphics import*
from Circuit_Simulator_Classes import*
import math
#initializes variables
def appStarted(app):
    app.margin = app.width//10
    app.spacing = 50
    app.gridDots = []
    app.dotR = 5
    setGridDots(app)
    app.selectedDot = []
    app.componentTypes = ["Wire", "DC Voltage Source", "Resistor", "Ground", "DC Current Source"]
    app.selectedComType = ""
    app.comTypeImages = [0]*len(app.componentTypes)
    setComTypeImages(app)
    app.boxWidth = app.margin*1.6
    app.boxHeight = 100
    app.selectingCom = True
    app.selectingNodes = False
    app.selectedNodes = []
    app.mouseX, app.mouseY = 0, 0
    app.sameStartAndEnd = False
    app.duplicateNodePairs = False
    app.newComponent = None
    app.selectedComponent = None 
    app.activeComponents = [[] for i in app.componentTypes]
    app.activeNodePairs = set()
    app.coordinateGraph = Graph()
    setCoordinateGraphNodes(app)
    app.netLists = []
    app.matricesList = []
    app.solutionsList = []
    app.settingVoltage = False
    app.invalidVoltage = False
    app.newVoltage = ""
    app.settingResistance = False
    app.invalidResistance = False
    app.newResistance = ""
    app.settingCurrent = False
    app.invalidCurrent = False
    app.newCurrent = ""
    app.run = False
    app.runBoxCoords = [app.width - app.margin/2 - app.spacing, app.spacing, 
                        app.width- app.spacing, app.spacing+app.margin/2]
    app.editBoxCoords = [app.width - app.margin - app.spacing, app.spacing, 
                        app.width- app.margin/2 - app.spacing, app.spacing+app.margin/2]
#creates grid of dots on which components can be places
def setGridDots(app):
    for i in range(app.margin*2, app.width, app.spacing):
        for j in range(app.margin*2, app.width, app.spacing):
            app.gridDots.append([i, j])
#converts pixel numbers into respective coordinate
def getGridDots(app, node):
    return [app.margin*2 + node[0]*app.spacing, app.margin*2 + node[1]*app.spacing]
#adds all grid dots as nodes in coordinate graph
def setCoordinateGraphNodes(app):
    for node in app.gridDots:
        nodeNum = ((node[0]-app.margin*2)//app.spacing, (node[1]-app.margin*2)//app.spacing)
        app.coordinateGraph.addNode(nodeNum)
#loads and scales images for each component type
def setComTypeImages(app):
    app.comTypeImages[0] = app.loadImage('Wire.png')
    app.comTypeImages[0] = app.scaleImage(app.comTypeImages[0], 1/5.5)
    app.comTypeImages[1] = app.loadImage('DC_Voltage_Source.png')
    app.comTypeImages[1] = app.scaleImage(app.comTypeImages[1], 1/16)
    app.comTypeImages[2] = app.loadImage('Resistor.png')
    app.comTypeImages[2] = app.scaleImage(app.comTypeImages[2], 1/10)
    app.comTypeImages[3] = app.loadImage('Ground.png')
    app.comTypeImages[3] = app.scaleImage(app.comTypeImages[3], 1/12)
    app.comTypeImages[4] = app.loadImage('DC_Current_Source.png')
    app.comTypeImages[4] = app.scaleImage(app.comTypeImages[4], 1/8)
#removes selected component from list of active components
def deleteComponent(app): 
    for cType in range(len(app.componentTypes)):
        if app.selectedComponent.flavor == app.componentTypes[cType]:
            app.activeComponents[cType].remove(app.selectedComponent)
            app.activeNodePairs.remove(listToTuple(app.selectedComponent.nodes))
            break  
#resets appropriate values and sets app to run analysis
def setToRunMode(app):
    app.run = True
    app.selectingCom = False
    app.selectingNodes = False
    app.sameStartAndEnd = False
    app.duplicateNodePairs = False
    app.newComponent = None
    app.selectedComponent = None 
    app.settingVoltage = False
    app.invalidVoltage = False
    app.newVoltage = ""
    app.settingResistance = False
    app.invalidResistance = False
    app.newResistance = ""
    app.settingCurrent = False
    app.invalidCurrent = False
    app.newCurrent = ""
#resets appropriate values and sets app to be able to place components and edit board
def setToEditMode(app):
    app.selectingCom = True
    app.run = False
    app.coordinateGraph = Graph()
    setCoordinateGraphNodes(app)
    app.netLists = []
    app.matricesList = []
    app.solutionsList = []
#takes x, y pixels and finds which component was clicked on
#sets app.selectedComponent
def findSelectedComponent(app, x, y):
    for cType in app.activeComponents:
        for aCom in cType:
            node1 = getGridDots(app, aCom.nodes[0])
            node2 = getGridDots(app, aCom.nodes[1])
            midX = (node1[0] + node2[0])/2
            midY = (node1[1] + node2[1])/2
            if (x >= midX - app.spacing/2 and x <= midX + app.spacing/2 and
                y >= midY - app.spacing/2 and y <= midY + app.spacing/2):
                app.selectedComponent = aCom
#controls all mouse actions
def mousePressed(app, event):
    x, y= event.x, event.y
    #if user clicks on run box, set to run mode
    if (x >= app.runBoxCoords[0] and 
        x <= app.runBoxCoords[2] and
        y >= app.runBoxCoords[1] and
        y <= app.runBoxCoords[3]):
        setToRunMode(app)
        runAnalysis(app)
    #if user clicks on edit box, set to edit mode
    elif (x >= app.editBoxCoords[0] and 
        x <= app.editBoxCoords[2] and
        y >= app.editBoxCoords[1] and
        y <= app.editBoxCoords[3]):
        setToEditMode(app)
    #finds component the user wants to see data of
    if app.run:
        findSelectedComponent(app, x, y)
        print(app.selectedComponent)
    #user has selected component and the app is in edit mode
    if app.selectedComponent != None and not app.run:
        #deletes selected component
        if x >= app.margin/10 and x <= app.margin*6/10 and y >= app.height-app.margin/2:
            deleteComponent(app)
        #modifies component attributes
        elif x >= app.margin*6/10 and x <= app.margin*11/10 and y >= app.height-app.margin/2:
            if isinstance(app.selectedComponent, DCVoltageSource):
                app.settingVoltage = True
            elif isinstance(app.selectedComponent, Resistor):
                app.settingResistance = True
            elif isinstance(app.selectedComponent, DCCurrentSource):
                app.settingCurrent = True
    #doesn't reset selected component if modifications are being made
    if not app.settingVoltage and not app.settingResistance and not app.settingCurrent and not app.run:
        app.selectedComponent = None 
    #chooses component type user wants to place
    if app.selectingCom:
        app.selectedComType = findComType(app, x, y)
        if app.selectedComType != "":
            app.selectingCom = False
            app.selectingNodes = True
        #if user doesn't choose a component, checks if user has selected a component to view data of
        else:
            findSelectedComponent(app, x, y)
    #user is selecting nodes of new component
    elif app.selectingNodes: 
        #cancels selecting nodes
        if x >= app.margin/10 and x <= app.margin*6/10 and y >= app.height-app.margin/2:
            app.selectedNodes = []
            app.selectingNodes = False
            app.selectingCom = True
        app.selectedDot = findDot(app, x, y)
        #only selects two points
        if len(app.selectedNodes) < 2 and app.selectedDot != []:
            #ground component is only connected to 1 node
            if app.selectedComType == app.componentTypes[3]:
                app.selectedNodes = [app.selectedDot]*2
            else:
                app.selectedNodes.append(app.selectedDot)
            #adds component object to list of active components
            if len(app.selectedNodes) == 2:
                nodesTuple = listToTuple(app.selectedNodes)
                #checks if start and end nodes are unique
                if app.selectedNodes[0] == app.selectedNodes[1] and app.selectedComType != app.componentTypes[3]:
                    app.sameStartAndEnd = True
                    app.selectedNodes.pop()
                #checks if nodes are already being used
                elif nodesTuple in app.activeNodePairs or (nodesTuple[1], nodesTuple[0]) in app.activeNodePairs:
                    app.duplicateNodePairs = True
                    app.selectedNodes.pop()
                #creates component object and resets app to selecting component type
                else:
                    app.sameStartAndEnd = False
                    app.duplicateNodePairs = False
                    app.activeNodePairs.add(nodesTuple)
                    if app.selectedComType == app.componentTypes[0]:
                        app.newComponent = Wire(app.selectedNodes)
                        app.activeComponents[0].append(app.newComponent)
                    elif app.selectedComType == app.componentTypes[1]:
                        app.newComponent = DCVoltageSource(app.selectedNodes, voltage = 9)
                        app.activeComponents[1].append(app.newComponent)
                    elif app.selectedComType == app.componentTypes[2]:
                        app.newComponent = Resistor(app.selectedNodes, resistance = 100)
                        app.activeComponents[2].append(app.newComponent)
                    elif app.selectedComType == app.componentTypes[3]:
                        app.newComponent = Ground(app.selectedNodes)
                        app.activeComponents[3].append(app.newComponent)
                    elif app.selectedComType == app.componentTypes[4]:
                        app.newComponent = DCCurrentSource(app.selectedNodes, current=1)
                        app.activeComponents[4].append(app.newComponent)
                    app.selectingNodes = False
                    app.selectingCom = True
                    app.selectedNodes = []
                    app.newComponent = None
#handles all key presses
def keyPressed(app, event):
    #depending on component type, correct attribute will be modified
    if app.settingVoltage:
        if event.key != "Enter":
            if not event.key.isnumeric() and not (event.key == "."):
                app.invalidVoltage = True
            else:
                app.newVoltage += event.key
        else:
            i = app.activeComponents[1].index(app.selectedComponent)
            app.activeComponents[1][i].voltage = round(float(app.newVoltage), 4)
            app.newVoltage = ""
            app.settingVoltage = False
            app.invalidVoltage = False
    elif app.settingResistance:
        if event.key != "Enter":
            if not event.key.isnumeric() and not (event.key == "."):
                app.invalidResistance = True
            else:
                app.newResistance += event.key
        else:
            i = app.activeComponents[2].index(app.selectedComponent)
            app.activeComponents[2][i].resistance = round(float(app.newResistance), 4)
            app.newResistance = ""
            app.settingResistance = False
            app.invalidResistance = False
    elif app.settingCurrent:
        if event.key != "Enter":
            if not event.key.isnumeric() and not (event.key == "."):
                app.invalidCurrent = True
            else:
                app.newCurrent += event.key
        else:
            i = app.activeComponents[4].index(app.selectedComponent)
            app.activeComponents[4][i].current = round(float(app.newCurrent), 4)
            app.newCurrent = ""
            app.settingCurrent = False
#handles mouse momvements
def mouseMoved(app, event):
    app.mouseX, app.mouseY = event.x, event.y
#runs circuit analysis
def runAnalysis(app):
    print("making graph")
    makeCoordinateGraph(app)
    for node in app.coordinateGraph.aList:
        if app.coordinateGraph.aList[node] != set():
            print(app.coordinateGraph.aList[node])
    makeNetLists(app)
    for netList in app.netLists:
        print("netList", netList.aList)
    makeMatricesList(app)
    for nodeMatrix in app.matricesList:
        print("nodeMatrix")
        print2dList(nodeMatrix.conductanceMatrix)
        print2dList(nodeMatrix.knownMatrix)
        print(nodeMatrix.componentVals)
    for solutionMatrix in app.solutionsList:
        print("solutionMatrix")
        if solutionMatrix != None:
            print2dList(solutionMatrix)
        else:
            print("Invalid Circuit")
#creates graph object with edges for all active components
def makeCoordinateGraph(app):
    for comType in range(len(app.activeComponents)):
        for aCom in range(len(app.activeComponents[comType])):
            node0 = tuple(app.activeComponents[comType][aCom].nodes[0])
            node1 = tuple(app.activeComponents[comType][aCom].nodes[1])
            app.coordinateGraph.addEdge(node0, node1, (comType, aCom))
#creates all circuit netlists
def makeNetLists(app):
    invalidNetLists = set()
    for g in range(len(app.activeComponents[3])):
        needNewNetList = True
        for i in range(len(app.netLists)):
            if tuple(app.activeComponents[3][g].nodes[0]) in app.netLists[i].aList:
                invalidNetLists.add(i)
                needNewNetList = False
        if needNewNetList:
            app.netLists.append(makeNetList(app, g))
    for i in invalidNetLists:
        app.netLists[i] = Graph()
    for netList in app.netLists:
        setNetListNeighbors(app, netList)
#connects nodes in circuit netlist graph across all active components in the netlist
def setNetListNeighbors(app, netList):
    for startNode in netList.aList:
        for neighbor in app.coordinateGraph.aList[startNode]:
            if neighbor[0] in netList.aList:
                netList.addEdge(startNode, neighbor[0], neighbor[1])
#determines all components connected to ground
def makeNetList(app, g):
    netList = Graph()
    for node in app.coordinateGraph.aList:
        solutions = None
        if app.coordinateGraph.aList[node] != set() and node not in netList.aList:
            solutions = findTwoUniquePaths(app, node, g)
        if solutions != None:
            for path in solutions:
                for node in path:
                    netList.addNode(node)
    return netList
#determines if the node is in a loop with the ground node
def findTwoUniquePaths(app, startNode, g):
    endNode = tuple(app.activeComponents[3][g].nodes[0])
    solutions = set()
    while(len(solutions) < 2):
        if startNode == endNode:
            return None
        solution = app.coordinateGraph.findUniquePath(startNode, endNode, solutions)
        if solution == None:
            return None
        else:
            solutions.add(solution)
    return solutions 
#creates all node matrices objects for all netlists 
def makeMatricesList(app):
    for netList in app.netLists:
        if len(netList.aList) != 0: 
              nodeMatrix = NodeMatrices(netList, app.activeComponents)
              nodeMatrix.setMatrices()
              solutionMatrix = nodeMatrix.solveMatrices()
              app.matricesList.append(nodeMatrix)
              app.solutionsList.append(solutionMatrix)
#finds which coordinate dot has been clicked on by user
def findDot(app, x, y):
    if x >= 2*app.margin-app.dotR*2 and y >= 2*app.margin-app.dotR*2:
        if ((x%app.spacing <= 10 or x%app.spacing >= 40) 
            and(y%app.spacing <= 10 or y%app.spacing >= 40)) :
            i = round(abs((x - 2*app.margin))/app.spacing)
            j = round(abs((y - 2*app.margin))/app.spacing)
            return [i, j]
    return []
#finds which box the user has clicked on which corresponds to a component type 
def findComType(app, x, y):
    if (x <= app.boxWidth and y >= app.margin*2 
        and y <= app.margin*2+app.boxHeight*len(app.componentTypes)):
        i = (y - app.margin*2)//app.boxHeight
        return app.componentTypes[i]
    return ""
#calculates distance between 2 points
def distance(x0, y0, x1, y1):
    return math.sqrt((x1-x0)**2 + (y1-y0)**2)
#calculates angle between two points and horizontal
def getAngle(nodes):
    if nodes[0] == nodes[1]:
        return 0
    x0, y0 = nodes[0][0], nodes[0][1]
    x1, y1 = nodes[1][0], nodes[1][1]
    angle = 180*(math.atan2(-(y1 -y0), x1 -x0))/math.pi
    return angle
#handles all drawing in the app
def redrawAll(app, canvas):
    drawTitle(app, canvas)
    drawGridDots(app, canvas)
    drawComponentTypes(app, canvas)
    drawNewComponent(app, canvas)
    drawActiveComponents(app, canvas)
    drawInstructions(app, canvas)
    drawComponentInfo(app, canvas)
    drawRun(app, canvas)
#draws name of app
def drawTitle(app, canvas):
    canvas.create_text(app.width/2, app.margin*2/3, 
                       text="Welcome to Circuit Simulator", font="Arial 30")
#draws coordinate grid
def drawGridDots(app, canvas):
    for dot in app.gridDots:
        canvas.create_oval(dot[0]-app.dotR, dot[1]-app.dotR, 
                           dot[0]+app.dotR, dot[1]+app.dotR, fill="black")
#draws boxes with each component type that can be chosen
def drawComponentTypes(app, canvas):
    canvas.create_text(app.margin*app.boxWidth/2, app.margin*1.8, text="Components", font="Arial 15")
    for c in range(len(app.componentTypes)):
        component = app.componentTypes[c]
        canvas.create_rectangle(0, app.margin*2+app.boxHeight*c, app.boxWidth, 
                                app.margin*2+app.boxHeight*(c+1), width=8)
        canvas.create_text(app.boxWidth/2, app.margin*2+app.boxHeight*(c+0.1), text = component)
        canvas.create_image(app.boxWidth/2, app.margin*2+app.boxHeight*(c+0.5), image =ImageTk.PhotoImage(app.comTypeImages[c]))
#draws instructions for corresponding task
def drawInstructions(app, canvas):
    canvas.create_text(5, 5, text="All circuits must be connected \nto ground and must only \nhave one ground per circuit", font="Arial 12", anchor="nw")
    if app.selectingCom:
        if app.settingVoltage:
            canvas.create_text(app.width/2, app.margin*4/3, 
                       text="Enter a numeric voltage and press enter when done", font="Arial 20")
            canvas.create_text(0, app.height-app.margin, text=f'New Voltage = {app.newVoltage} V', 
                               font="Arial 10", anchor="w")
        elif app.settingResistance:
            canvas.create_text(app.width/2, app.margin*4/3, 
                       text="Enter a numeric resistance and press enter when done", font="Arial 20")
            canvas.create_text(0, app.height-app.margin, text=f'New Resistance = {app.newResistance} ohms', 
                               font="Arial 10", anchor="w")
        elif app.settingCurrent:
            canvas.create_text(app.width/2, app.margin*4/3, 
                       text="Enter a numeric current and press enter when done", font="Arial 20")
            canvas.create_text(0, app.height-app.margin, text=f'New Current = {app.newCurrent} A', 
                               font="Arial 10", anchor="w")
        else:
            canvas.create_text(app.width/2, app.margin*4/3, 
                               text="Select a component and place it on the board", font="Arial 20")
    elif app.selectingNodes:
        canvas.create_rectangle(app.margin/10, app.height-app.margin/2, app.margin*6/10, app.height, width=3)
        canvas.create_text(app.margin*3.5/10, app.height-app.margin/4, text="Cancel", font="Arial 10", anchor="center")
        if len(app.selectedNodes) == 0:
            canvas.create_text(app.width/2, app.margin*4/3, 
                       text="Select the starting coordinate", font="Arial 20") 
        elif len(app.selectedNodes) == 1:
            if app.sameStartAndEnd:
                canvas.create_text(app.width/2, app.margin*4/3, 
                       text="The ending coordinate must be different from the starting coordinate", font="Arial 20")    
            elif app.duplicateNodePairs:
                canvas.create_text(app.width/2, app.margin*4/3, 
                       text="Components cannot occupy the same locations", font="Arial 20")
            else:
                canvas.create_text(app.width/2, app.margin*4/3, 
                       text="Select the ending coordinate", font="Arial 20") 
    elif app.run:
        canvas.create_text(app.width/2, app.margin*4/3, 
                       text="Click on components to see component voltages and current", font="Arial 20")
#draws active components on the board
#draws rotated component image with lines connecting image to corresponding nodes
def drawNewComponent(app, canvas):
    if len(app.selectedNodes) == 1:
        if app.selectedComType == "Wire":
            comType = 0
        elif app.selectedComType == "DC Voltage Source":
            comType = 1
        elif app.selectedComType == "Resistor":
            comType = 2
        elif app.selectedComType == "Ground":
            comType = 3
        elif app.selectedComType == "DC Current Source":
            comType = 4
        node1 = getGridDots(app, app.selectedNodes[0])
        midX = (node1[0]+app.mouseX)/2
        midY = (node1[1]+app.mouseY)/2
        angle = getAngle([node1, [app.mouseX, app.mouseY]])
        d = distance(node1[0], node1[1], app.mouseX, app.mouseY)
        canvas.create_image(midX, midY, image =ImageTk.PhotoImage(app.comTypeImages[comType].rotate(angle)))
        if d > 51:
            dprime = (d- app.spacing+10)/2
            offsetX = dprime*math.cos(angle*math.pi/180)
            offsetY = dprime*math.sin(angle*math.pi/180)
            canvas.create_line(node1[0], node1[1],
                               node1[0]+offsetX, node1[1]-offsetY, width=2)
            canvas.create_line(app.mouseX-offsetX, app.mouseY+offsetY, 
                               app.mouseX, app.mouseY, width=2)
            if comType == 0:
                canvas.create_line(node1[0]+offsetX, node1[1]-offsetY,
                                   app.mouseX-offsetX, app.mouseY+offsetY, width=3, fill="red")
        else:
            if comType == 0:
                canvas.create_line(node1[0], node1[1], app.mouseX, app.mouseY, width=3, fill="red")
def drawActiveComponents(app, canvas):
    for comType in range(len(app.activeComponents)):
        for com in app.activeComponents[comType]:
            node1 = getGridDots(app, com.nodes[0])
            node2 = getGridDots(app, com.nodes[1])
            midX = (node1[0]+node2[0])/2
            midY = (node1[1]+node2[1])/2
            angle = getAngle(com.nodes)
            d = distance(node1[0], node1[1], node2[0], node2[1])
            if comType == 3:
                midY += app.spacing/2
            canvas.create_image(midX, midY, image =ImageTk.PhotoImage(app.comTypeImages[comType].rotate(angle)))
            if d > 51:
                dprime = (d- app.spacing+10)/2
                offsetX = dprime*math.cos(angle*math.pi/180)
                offsetY = dprime*math.sin(angle*math.pi/180)
                canvas.create_line(node1[0], node1[1],
                                   node1[0]+offsetX, node1[1]-offsetY, width=2)
                canvas.create_line(node2[0]-offsetX, node2[1]+offsetY, 
                                   node2[0], node2[1], width=2)
                if comType == 0:
                    canvas.create_line(node1[0]+offsetX, node1[1]-offsetY,
                                       node2[0]-offsetX, node2[1]+offsetY, width=3, fill="red")
            else:
                if comType == 0:
                    canvas.create_line(node1[0], node1[1], node2[0], node2[1], width=3, fill="red")
#draws selected component values
def drawComponentInfo(app, canvas):
    if app.selectedComponent != None:
        canvas.create_text(5, app.height-app.margin, text=f'{app.selectedComponent}', font="Arial 9", anchor="sw")
        if app.selectingCom:
            canvas.create_rectangle(app.margin/10, app.height-app.margin/2, app.margin*6/10, app.height, width=3)
            canvas.create_text(app.margin*3.5/10, app.height-app.margin/4, text="Delete", font="Arial 10")
        if isinstance(app.selectedComponent, Wire):
            if app.run:
                i = app.activeComponents[0].index(app.selectedComponent)
                for nodeMatrix in app.matricesList:
                    if (0, i) in nodeMatrix.componentVals:
                        canvas.create_text(5, app.height-app.margin/2, text=(f'Voltage at {app.selectedComponent.nodes[0]} = {nodeMatrix.componentVals[(0,i)][0]}\n'
                        f'Voltage at {app.selectedComponent.nodes[1]} = {nodeMatrix.componentVals[(0,i)][1]}\n'
                        f'Component current = {nodeMatrix.componentVals[(0,i)][2]}'), font="Arial 9", anchor="sw")        
        elif isinstance(app.selectedComponent, DCVoltageSource):
            if app.selectingCom:
                canvas.create_rectangle(app.margin*6/10, app.height-app.margin/2, app.margin*11/10, app.height, width=3)
                canvas.create_text(app.margin*8.5/10, app.height-app.margin/4, text="   Set\nVoltage", font="Arial 10", anchor="center")
            if app.run:
                i = app.activeComponents[1].index(app.selectedComponent)
                for nodeMatrix in app.matricesList:
                    if (1, i) in nodeMatrix.componentVals:
                        canvas.create_text(5, app.height-app.margin/2, text=(f'Voltage at {app.selectedComponent.nodes[0]} = {nodeMatrix.componentVals[(1,i)][0]}\n'
                        f'Voltage at {app.selectedComponent.nodes[1]} = {nodeMatrix.componentVals[(1,i)][1]}\n'
                        f'Component current = {nodeMatrix.componentVals[(1,i)][2]}'), font="Arial 9", anchor="sw")     
        elif isinstance(app.selectedComponent, Resistor):
            if app.selectingCom:
                canvas.create_rectangle(app.margin*6/10, app.height-app.margin/2, app.margin*11/10, app.height, width=3)
                canvas.create_text(app.margin*8.5/10, app.height-app.margin/4, text="   Set\nResistance", font="Arial 7", anchor="center")
            if app.run:
                i = app.activeComponents[2].index(app.selectedComponent)
                for nodeMatrix in app.matricesList:
                    if (2, i) in nodeMatrix.componentVals:
                        canvas.create_text(5, app.height-app.margin/2, text=(f'Voltage at {app.selectedComponent.nodes[0]} = {nodeMatrix.componentVals[(2,i)][0]}\n'
                        f'Voltage at {app.selectedComponent.nodes[1]} = {nodeMatrix.componentVals[(2,i)][1]}\n'
                        f'Component current = {nodeMatrix.componentVals[(2,i)][2]}'), font="Arial 9", anchor="sw")        
        elif isinstance(app.selectedComponent, Ground):
            if app.run:
                i = app.activeComponents[3].index(app.selectedComponent)
                for nodeMatrix in app.matricesList:
                    if (3, i) in nodeMatrix.componentVals:
                        canvas.create_text(5, app.height-app.margin/2, text=(f'Voltage at {app.selectedComponent.nodes[0]} = {nodeMatrix.componentVals[(3,i)][0]}\n'
                        f'Voltage at {app.selectedComponent.nodes[1]} = {nodeMatrix.componentVals[(3,i)][1]}\n'
                        f'Component current = {nodeMatrix.componentVals[(3,i)][2]}'), font="Arial 9", anchor="sw")       
        elif isinstance(app.selectedComponent, DCCurrentSource):
            if app.selectingCom:
                canvas.create_rectangle(app.margin*6/10, app.height-app.margin/2, app.margin*11/10, app.height, width=3)
                canvas.create_text(app.margin*8.5/10, app.height-app.margin/4, text="   Set\nCurrent", font="Arial 7", anchor="center")
            if app.run:
                i = app.activeComponents[4].index(app.selectedComponent)
                for nodeMatrix in app.matricesList:
                    if (4, i) in nodeMatrix.componentVals:
                        canvas.create_text(5, app.height-app.margin/2, text=(f'Voltage at {app.selectedComponent.nodes[0]} = {nodeMatrix.componentVals[(4,i)][0]}\n'
                        f'Voltage at {app.selectedComponent.nodes[0]} = {nodeMatrix.componentVals[(4,i)][1]}\n'
                        f'Component current = {nodeMatrix.componentVals[(4,i)][2]}'), font="Arial 9", anchor="sw")
#draws boxes to set app to edit and run mode
def drawRun(app, canvas):
    if app.run:
        runFill = "green"
        editFill = "white"
    else:
        runFill = "white"
        editFill = "green"
    canvas.create_rectangle(app.runBoxCoords[0], app.runBoxCoords[1],
                            app.runBoxCoords[2], app.runBoxCoords[3], width=3, fill= runFill)
    canvas.create_text((app.runBoxCoords[0] + app.runBoxCoords[2])/2, (app.runBoxCoords[1] + app.runBoxCoords[3])/2, text="Run", font="Arial 15")
    canvas.create_rectangle(app.editBoxCoords[0], app.editBoxCoords[1],
                            app.editBoxCoords[2], app.editBoxCoords[3], width=3, fill = editFill)
    canvas.create_text((app.editBoxCoords[0] + app.editBoxCoords[2])/2, (app.editBoxCoords[1] + app.editBoxCoords[3])/2, text="Edit", font="Arial 15")
runApp(width= 1000, height= 1000)