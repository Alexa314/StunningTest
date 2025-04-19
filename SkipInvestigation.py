import numpy as np
import math

def addFrame(timeActive,deltaTime = np.single(0.0166667)):
    #Adds a frame
    timeActive = np.single(timeActive)
    deltaTime = np.single(deltaTime)
    if type(timeActive)!=np.float32:
        print("Uh Oh!, tA not 32!")
        print(1/0)
    elif type(deltaTime)!=np.float32:
        print("Uh Oh!, dT not 32!")
        print(1/0)
    else:
        return(np.single(np.double(timeActive) + np.double(deltaTime)))

def addFrames(timeActive,deltaTime,amount):
    #Adds multiple frames
    tA = timeActive
    for _ in range(amount):
        tA = addFrame(tA,deltaTime)
    return(tA)

def pause(timeActive,deltaTime):
    #Adds 10 frames, like a pause
    return(addFrames(timeActive,deltaTime,10))

def onInterval(timeActive, deltaTime, offset, interval = np.single(0.05)):
    #Checks if a spinner will load
    lastFrame = math.floor((np.double(timeActive) - np.double(offset) - np.double(deltaTime))/np.double(interval))
    currentFrame = math.floor((np.double(timeActive) - np.double(offset))/np.double(interval))
    return(lastFrame < currentFrame)

def onIntervalNumbers(timeActive, deltaTime, offset, interval = np.single(0.05)):
    #Produces the exact numbers for onInterval.
    lastFrame = (np.double(timeActive) - np.double(offset) - np.double(deltaTime))/np.double(interval)
    currentFrame = (np.double(timeActive) - np.double(offset))/np.double(interval)
    return(math.floor(lastFrame),math.floor(currentFrame),lastFrame,currentFrame)


def tryEverything(start = 0,jumpPowers = False,offset = np.single(0), cap = 3000):
    #Checks every single float value from start to cap to see if they work for spinner loading.
    validPoints = []
    if start!=0:
        currentPower = max(round(math.log(start,2)),1)
    initial = np.single(start)
    epsilon = np.single(np.finfo(initial).eps)
    while True:
        try:
            if jumpPowers and (initial > 2**currentPower + 1 or initial >= 2**(currentPower+1)):
                currentPower += 1
                initial = np.single(2**currentPower)
            while initial+epsilon == initial:
                epsilon*=2
                epsilon = np.single(epsilon)
            initial = np.single(initial + epsilon)
            if crucialPoint(initial,offset):
                if crucialPoint(initial - np.single(1),offset) and crucialPoint(initial+np.single(1),offset):
                    pass
                if not crucialPoint(initial-np.single(1),offset):
                    print(initial,'works but ',initial-np.single(1),'doesn\'t!')
                elif not crucialPoint(initial+np.single(1),offset):
                    print(initial,'works but ',initial+np.single(1),'doesn\'t :(')
                elif initial - start < 1:
                    print(initial,'works!')
                validPoints.append(initial)
            if initial > cap:
                return(validPoints)
        except KeyboardInterrupt:
            input(str(initial)+'   '+str(epsilon))

def crucialPoint(singlePoint,offset):
    #Informs you if TA = singlePoint for spinner wtih offset gets a badeline skip
    dTOne = np.single(0.014682573)
    dTTwo = np.single(0.014880986)
    if onIntervalNumbers(singlePoint,dTOne,offset)[1] < onIntervalNumbers(addFrame(singlePoint,dTTwo),dTTwo,offset)[0]:
        return(True)
    
def createFile(fileName,offset):
    #creates a file with the output of tryEverything.
    items = tryEverything(20,False,np.single(offset))
    file = open(fileName,'w')
    _ = file.write(str(items)[1:-1])
    file.close()

def tryPowers(offset,starting = 64,outPrint = True):
    #Checks the region of all powers from starting until 4096.
    starting = np.single(starting)
    validPowers = set()
    curPower = np.single(starting)
    curEpsilon = np.single(2**(-20))
    while np.single(starting + curEpsilon) == starting:
        curEpsilon = np.single(curEpsilon * 2)
    while curPower < 4096:
        while starting-curPower < .3:
            starting = np.single(starting + curEpsilon)
            if crucialPoint(starting,offset):
                if outPrint:
                    print(starting)
                validPowers.add(curPower)
        curPower = np.single(curPower * 2)
        curEpsilon = np.single(curEpsilon * 2)
        starting = curPower
    return(validPowers)

def getFirst1024(offset,starting=1024):
    #Finds the first moment after 1024 which works
    starting = np.single(starting)
    epsilon = np.single(2**(-13))
    while starting < 2048:
        if crucialPoint(starting,offset):
            return(starting)
        starting = np.single(starting+epsilon)

def forcePauses(initialTA,deltaTimes,offset):
    #Brute force pausing
    currentPath = 0
    maxDepth = 0
    frameCount = len(deltaTimes)
    while currentPath < 2 ** frameCount:
        pauses = str(bin(currentPath))[2:]
        pauses = '0'*(frameCount-len(pauses))+pauses
        timeActive = initialTA
        for i in range(frameCount):
            if pauses[i]=='1':
                timeActive = addFrames(timeActive,deltaTimes[i],10)
            timeActive = addFrame(timeActive,deltaTimes[i])
            loadCheck = onInterval(timeActive,deltaTimes[i],offset,np.single(0.05))
            if loadCheck:
                break
            if i == frameCount - 1:
                i += 1
        if i == frameCount:
            break
        maxDepth = max(maxDepth,i)
        amount = 2**(frameCount - i-1)
          #  print(amount,i)
        #input(str([i,frameCount,pauses,timeActive,loadCheck]))
        currentPath-=currentPath%amount
        currentPath+=amount
    if i != frameCount:
        return(False,i)
    return(currentPath,timeActive)

def badelineThrow(pauseSequence,initialTA,offset,verbose = False):#√
    global badelineThrowDT
    timeActive = initialTA
    deltaTime = [np.single(0.012500024401), np.single(0.012698438019), np.single(0.012896850705), np.single(0.013095265254), np.single(0.013293678872), np.single(0.013492091559), np.single(0.013690506108), np.single(0.013888919726), np.single(0.014087333344), np.single(0.014285746031), np.single(0.014484159648), np.single(0.014682573266), np.single(0.014880985953), np.single(0.015079400502), np.single(0.015277813189), np.single(0.015476226807), np.single(0.015674641356), np.single(0.015873054042), np.single(0.016071466729), np.single(0.016269881278), np.single(0.016468293965)]
    success = True
    for i in range(len(deltaTime)):
        if pauseSequence[i] == '1':
            timeActive = pause(timeActive,deltaTime[i])
        timeActive = addFrame(timeActive,deltaTime[i])
        loadCheck = onInterval(timeActive,deltaTime[i],offset,np.single(0.05))
        if loadCheck:
            success = False
            return(False)
        if verbose:
            print(', '.join([str(item) for item in [i, loadCheck,timeActive,(timeActive*60)%3,deltaTime[i],onIntervalNumbers(timeActive,deltaTime[i],offset,np.single(0.05))]]))
    return(success)

def backTrack(timeActives,endGoals):
    #Finds all timeactives that lead to an endGoal after going through timeActives.
    if type(endGoals) == list:
        possibles = endGoals.copy()
    else:
        possibles = [endGoals]
    reversedTA = list(reversed(timeActives))
    for i in range(len(timeActives)):
        oldPossibles = possibles.copy()
        possibles = []
        deltaTime = reversedTA[i]
        minimumGuess = min(oldPossibles) - deltaTime - np.single(0.0002)
        maximumGuess = max(oldPossibles) - deltaTime + np.single(0.0001)
        currentGuess = minimumGuess
        epsilon = np.single(2**(-40))
        while currentGuess <= maximumGuess:
            while np.single(currentGuess + epsilon) == currentGuess:
                epsilon*=2
            currentGuess = np.single(currentGuess + epsilon)
            if addFrame(currentGuess,deltaTime) in oldPossibles:
                possibles.append(currentGuess)
    return(possibles)

def normalize(timeList,normalizeCap = -1,deltaTime = np.single(0.0166667)):
    #Take multiple times and put them all in the same timerange
    if normalizeCap == -1:
        normalizeCap = min(timeList) - .0005
    normalized = []
    toDo = timeList.copy()
    while len(toDo)!=0:
        newToDo = []
        for item in toDo:
            if item < normalizeCap:
                normalized.append(item)
            else:
                newToDo.extend(backTrack([deltaTime],item))
        toDo = newToDo.copy()
    if max(normalized) - min(normalized) > deltaTime / 3:
        print("This is a very large range of normalization, beware")
    return(normalized)


def fullRoom(initialTA,offset = 0,verbose = False):
    #An example of checking if a stun will work from the start.
    offset = np.single(offset)
    initialTA = forcePauses(initialTA,[np.single(0.0166667)]*14,offset)[1]
    if verbose:
        print(initialTA)
    initialTA = forcePauses(initialTA,[np.single(0.0125)]*10,offset)[1]
    if verbose:
        print(initialTA)
    for path in ['101111111111011111110', '101111111111011111001', '101111111111000100101', '101111111111010100101', '101111111111001100101', '011111111111011111110', '011111111111011111001', '011111111111000100101', '011111111111010100101', '011111111111001100101', '001111111111011111110', '001111111111011111001', '001111111111000100101', '001111111111010100101', '001111111111001100101', '111111111111011111110', '111111111111011111001', '111111111111000100101', '111111111111010100101', '111111111111001100101']:
        if badelineThrow(path,initialTA,offset):
            _ = badelineThrow(path,initialTA,offset,verbose)
            return(True,path)
        
def produceValid(function, start, stop, doPrints = False):
    #Print all float values which satisfy some function.
    epsilon = 2**(-30)
    start = np.single(start)
    stop = np.single(stop)
    valids = []
    while start + epsilon == start:
        epsilon = np.single(2 * epsilon)
    while start < stop:
        start = np.single(start + epsilon)
        if function(start):
            valids.append(start)
            if doPrints:
                print(start)
    return(valids)


def allPrecursors(endGoal,deltaTime = np.single(0.0166667),minimumStart = np.single(0)):
    #Gets every float value wthat will eventually reach one of endGoal.
    if type(endGoal) == list:
        newP = [np.single(item) for item in endGoal]
    else:
        newP = [np.single(endGoal)]
    deltaTime,minimumStart = np.single(deltaTime),np.single(minimumStart)
    precursors = []
    while max(newP) > minimumStart:
        precursors.extend(newP)
        newP = backTrack([deltaTime],newP)
    return(precursors)

def distances(validList,currentThing,verbose = False):
    #Tells you the nearest elements to currentThing in validList
    i = len(validList)//2
    currentDelta = i//2
    while abs(currentThing - validList[i]) > 1/60:
        i += currentDelta * (-1)**(currentThing > validList[i])
        currentDelta //= 2
        if verbose:
            print(i,currentDelta,validList[i],currentThing)
    withinFrames = []
    minRange = -20
    maxRange = 20
    while abs(validList[i+minRange] - currentThing) < 1/90:
        if verbose:
            input(minRange)
        minRange-=1
    while abs(validList[i+maxRange] - currentThing) < 1/90:
        if verbose:
            input(maxRange)
        maxRange+=1
    if verbose:
        print(minRange,maxRange)
    for j in range(minRange,maxRange):
        if abs(validList[i+j] - currentThing) < 1/90:
            withinFrames.append(validList[i+j])
    return(withinFrames)

def printDistances(validList,currentThing):
    #prints your distance from a valid result, along with 60x that. 
    distanceList = distances(validList,currentThing)
    for item in distanceList:
        print(item,item-currentThing, (item-currentThing)*60, (item-currentThing)*60 * 84)
