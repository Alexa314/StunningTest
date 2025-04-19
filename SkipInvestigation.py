import numpy as np
import math

def addFrame(timeActive,deltaTime):
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
