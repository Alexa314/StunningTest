import os
import numpy as np
import math
###Section 1: Label Processing
    #Use this to analyze the room dash counts of a file
def getProcessedLabels(fileName,wantLines = False):
    #This function takes a file and returns a list containing [room name, dash count]
    #Specifically it looks for anything of the following format:
    #Either #????     or ??? read ???
    #       ?1235x       ?1235x
    #Where ?'s can be anything.
    openedFile = open(fileName)
    lines = ['\n']
    while lines[-1]!='':
        lines.append(openedFile.readline())
    openedFile.close()
    roomLabels = []
    for i in range(len(lines)):
        if '#' in lines[i] or 'read' in lines[i].lower():
            try:
                if len(lines[i+1])<=1:
                    pass
                elif lines[i+1][1].isnumeric() and 'x' in lines[i+1]:
                    roomLabels.append([lines[i],lines[i+1]])
            except:
                print(lines[i],lines[i+1],lines[i+2])
    processedLabels = []
    for room in roomLabels:
        proccessed = [room[0][:-1],int(room[1].split('x')[0][1:])]
        processedLabels.append(proccessed.copy())
    if wantLines:
        return(processedLabels,lines)
    return(processedLabels)
def getPL(fN,wL=False):
    #shorter alias
    return(getProcessedLabels(fN,wL))
def printRoomCounts(fileName,verbose = True,dashStart = 0, dashEnd = 99999 ):
    #This takes a file and prints out the amount of dashes you should have when entering each room
    #(If not verbose, only the amount to finish the TAS)
    #Furthermore, you can use the later variables to only print dash counts between specific sections
    #Useful for debugging inconsistencies
    processedLabels,lines = getPL(fileName,True)
    currentCount = 0
    for item in processedLabels:
        if verbose and currentCount >= dashStart and currentCount <= dashEnd:
            print('Enter ' + item[0] + ' with ' + str(currentCount) + ' dashes!')
        currentCount += item[1]
    print('Exit level with ' + str(currentCount) + ' dashes!')
    print(lines[1])

def printNonZeroRC(fileName):
    #Only prints out the rooms that aren't 0x
    processedLabels = getPL(fileName)
    for item in processedLabels:
        if item[1]!=0:
            print('You dash '+str(item[1])+' times in '+item[0])
            
###Section 2: Unrestricted Calculations
    #Use this to help you make the set commands for unrestricted waits
deltaTime = np.single(0.0166667)
spinPAValues = [[0, np.single(0.0166667)], [1, np.single(0.0333334)], [3, np.single(0.0666668)], [7, np.single(0.13333358)], [14, np.single(0.25000045)], [29, np.single(0.5000011)], [59, np.single(1.0000024)], [119, np.single(2.0000014)], [240, np.single(4.0166664)], [479, np.single(8.000052)], [960, np.single(16.016598)], [1920, np.single(32.016354)], [3840, np.single(64.01587)], [7679, np.single(128.01286)], [15361, np.single(256.01495)], [30724, np.single(512.00244)], [61452, np.single(1024.0107)], [122683, np.single(2048.0154)], [246044, np.single(4096.001)], [492768, np.single(8192.005)], [986216, np.single(16384.014)], [1918283, np.single(32768.004)], [4015435, np.single(65536.01)], [8209739, np.single(131072.02)], [16598346, np.single(262144.0)], [24986954, np.single(524288.0)]]
freezeValue = [24986954, np.single(524288.0)]
thousandCorpus = []
spinPAValues.extend(thousandCorpus)
goalValues = set([item[1] for item in spinPAValues])

def ensureSingle(*args):
    #Ensures variables are np.singles, for the correct float behavior
    newArgs = (np.single(item) if type(item)!=np.float32 else item for item in args)
    return(newArgs)

def addFrame(timeActive,deltaTime = np.single(0.0166667)):
    #All of this casting probably isn't necessary but this guarantees perfect accuracy
    timeActive, deltaTime = ensureSingle(timeActive, deltaTime)
    return(np.single(np.double(timeActive) + np.double(deltaTime)))

def subtractFrame(timeActive,deltaTime = np.single(0.0166667)):
    #No guarantees on accuracy for values that aren't on the timeActive .0166667 grid
    #Will work after 262144 for sure which is the only place this is used
    timeActive, deltaTime = ensureSingle(timeActive, deltaTime)
    result = np.single(np.double(timeActive) - np.double(deltaTime))
    return(result)
    
def framesTillFreeze(timeActive):
    #Says how many frames till TA hits 524288
    timeActive = ensureSingle(timeActive).__next__()
    addedFrames = 0
    while timeActive not in goalValues:
        addedFrames+=1
        timeActive = addFrame(timeActive)
    frameCount = [item[0] for item in spinPAValues if item[1]==timeActive][0]
    frameCount -= addedFrames
    remainingFrames = freezeValue[0]-frameCount
    return(remainingFrames)

def generateWait(startingTimeActive,startingFrameCount,goalTimeActive = 524288):
    #Produces the 3 commands required for a wait
    #Command 1: console evallua ...  changes filetime - not necessary for individual levels, but crucial for fullgame things
    #Command 2: Set TimeActive is pretty clear what it does, sets the timeactive
    #Command 3: Set Session.Time updates the current level timer to the appropriate value
    startingTimeActive, goalTimeActive = ensureSingle(startingTimeActive,goalTimeActive)
    startingFTF = framesTillFreeze(startingTimeActive)
    endingFTF = framesTillFreeze(goalTimeActive)
    totalFrames = startingFTF - endingFTF
    print('console EvalLua Celeste.SaveData.Instance:AddTime(session.Area, '+str(totalFrames)+' * 170000)')
    print("Set, Level.TimeActive, " + str(np.double(goalTimeActive)))
    print("Set, Session.Time, " + str(170000 * (startingFrameCount + totalFrames)))

def cycleWait(startingTimeActive,startingFrameCount,cycleLength, goalTimeActive = 524288):
    #This adds in the ability to work with a for loop
    #Or perhaps you can use this to see how this lines up with other cycles that might be happening in the room (like dust bunnies)
    startingTimeActive, goalTimeActive = ensureSingle(startingTimeActive,goalTimeActive)
    startingFTF = framesTillFreeze(startingTimeActive)
    endingFTF = framesTillFreeze(goalTimeActive)
    totalFrames = startingFTF - endingFTF
    cycleCount = totalFrames // cycleLength
    remainingFrames = totalFrames % cycleLength
    totalFrames = totalFrames - remainingFrames
    newGoalTimeActive = goalTimeActive
    for _ in range(remainingFrames):
        newGoalTimeActive = subtractFrame(newGoalTimeActive)
    print("console EvalLua Celeste.SaveData.Instance:AddTime(session.Area, '+str(totalFrames)+' * 170000)")
    print("Set, Level.TimeActive, " + str(np.double(newGoalTimeActive)))
    print("Set, Session.Time, " + str(170000 * (startingFrameCount + totalFrames)))
    print("This consisted of "+str(cycleCount)+" loops and there remains "+str(remainingFrames)+" frames to wait before your value")


###Section 3: Showcase Preparation
    #Use this to help prepare SR files for showcases (doesn't help with U waits)
def giveLongInputs(fileName,thresholdSingle = 200,thresholdRepeat = 500, printifTrueelseInput = True):
    #repeat hasn't been tested
    #regardless, should tell you where long waits/repeats are
    #useful for finding places to speedup
    #Example command pair:
#console display_message Speed 1.3 40 False Speeding up 15x
#Set, TASRecorder.Speed, 15.0

#Set, TASRecorder.Speed, 1.0
#console hide_message Speed
    totalLength = 0
    openedFile = open(fileName)
    lines = ['\n']
    while lines[-1]!='':
        lines.append(openedFile.readline())
    openedFile.close()
    roomLabels = []
    for i in range(len(lines)):
        line = lines[i]
        while len(line)>0 and line[0] == ' ':
            line = line[1:]
        j = 0
        if 'repeat' in line.lower()[:8]:
            while j<len(line)-2 and not line[j].isnumeric():
                j+=1
            if j!=len(line)-2:
                repeatCount = int(line[j:])
                totalFrames = 0
                findingEnd = i+1
                while 'repeat' not in lines[findingEnd].lower():
                    try:
                        totalFrames+=int(lines[findingEnd].split()[0].split(',')[0])
                    except:
                        pass 
                    findingEnd+=1
                if repeatCount * totalFrames >= thresholdRepeat:
                    totalLength += repeatCount * totalFrames
                    if printifTrueelseInput:
                        print(line[:-1] + ' [total length is '+str(repeatCount*totalFrames)+']',end = '\n')
                    else:
                        input(line[:-1] + ' [total length is '+str(repeatCount*totalFrames)+']')
        else:
            while line[:j+1].isnumeric():
                j+=1
                if len(line)<j:
                    break
            if j>0:
                if len(line)<j:
                    j+=1
                if int(line[:j]) > thresholdSingle:
                    if printifTrueelseInput:
                        print(line, end = '')
                    else:
                        input(line[:-1])
                    totalLength += int((line+',').split(',')[0])
    print("Total Wait is ",totalLength)

def addStunningLabels(fileName,addHitboxes = True):
    startingMessage = "console display_message Stunning 1.3 40 False Stunning \n"
    if addHitboxes:
        startingMessage = "Set, CelesteTAS.ShowHitboxes, True \n" + startingMessage
    endingMessage = "console hide_message Stunning \n"
    if addHitboxes:
        endingMessage = "Set, CelesteTAS.ShowHitboxes, False \n" + endingMessage
    with open(fileName,'r+') as file:
        fileLines = file.readlines()
        newFileLines = []
        for item in fileLines:
            if "stunpause" in item.lower() and "mode" not in item.lower():
                if '#' not in item:
                    if 'end' in item.lower():
                        newFileLines.append(item)
                        newFileLines.append(endingMessage)
                    else:
                        newFileLines.append(startingMessage)
                        newFileLines.append(item)
            else:
                newFileLines.append(item)
        file.seek(0)
        file.writelines(newFileLines)

def removeLinesSatisfying(fileName,boolFunction):
    with open(fileName,'r+') as file:
        fileLines = file.readlines()
        newFileLines = []
        for item in fileLines:
            if boolFunction(item):
                continue
            newFileLines.append(item)
        file.seek(0)
        file.writelines(newFileLines)
        file.truncate()

def makeEvalLua(fileName):
    with open(fileName,'r+') as file:
        fileLines = file.readlines()
        newFileLines = []
        for item in fileLines:
            if "SaveData.Instance.AddTime" in item:
                item = item.lower()
                item = item.replace('evalcs','EvalLua')
                item = item.replace('SaveData.Instance.AddTime((Monocle.Engine.Scene as Level).Session.Area, '.lower(),"Celeste.SaveData.Instance:AddTime(session.Area, ")
                item = item.replace("170000l)","170000)")            
            newFileLines.append(item)
        file.seek(0)
        file.writelines(newFileLines)
        file.truncate()

def makeSpeedupsPlayable(fileName):
    with open(fileName,'r+') as file:
        fileLines = file.readlines()
        newFileLines = []
        currentSpeed = 1
        for item in fileLines:
            if 'tasrecorder.speed' in item.lower():
                newFileLines.append('***{}\n'.format(currentSpeed))
                if ',' in item:
                    currentSpeed = int(float(item.split(',')[-1].split()[0]))
                else:
                    currentSpeed = int(float(item.split()[-1]))
            newFileLines.append(item)
        newFileLines.append('\n***1\n')
        file.seek(0)
        file.writelines(newFileLines)
        file.truncate()

def addHitboxCommand(fileName):
    with open(fileName,'r+') as file:
        fileLines = file.readlines()
        newFileLines = []
        currentSpeed = 1
        for item in fileLines:
            if 'display_message stunning' in item.lower():
                newFileLines.append('Set, CelesteTAS.ShowHitboxes, True\n')
            elif 'hide_message stunning' in item.lower():
                newFileLines.append('Set, CelesteTAS.ShowHitboxes, False\n')    
            newFileLines.append(item)
        file.seek(0)
        file.writelines(newFileLines)
        file.truncate()

def getFiles(directory):
    files = []
    for file in os.listdir(directory):
        if '.' in file:
            files.append(directory+'/'+file)
        else:
            files.extend(getFiles(directory+'/'+file))
    return(files)

def fullDirectory(directory,function):
    files = getFiles(directory)
    for item in files:
        function(item)


removeDisplayMessages = lambda x: removeLinesSatisfying(x, lambda item: 'display_message' in item.lower() or 'hide_message' in item.lower())
removeTASRecorderSpeed = lambda x: removeLinesSatisfying(x, lambda item: 'tasrecorder.speed' in item.lower())
removeTASRecorderFades = lambda x: removeLinesSatisfying(x, lambda item: 'tasrecorder.blackfade' in item.lower())
    


###Section 4: Stun Making
    #Use this as an assist for badeline throws and oshiro slowdowns
global badelineThrowDT
badelineThrowDT = [np.single(0.012500024401),
                   np.single(0.012698438019),
                   np.single(0.012896850705),
                   np.single(0.013095265254),
                   np.single(0.013293678872),
                   np.single(0.013492091559),
                   np.single(0.013690506108),
                   np.single(0.013888919726),
                   np.single(0.014087333344),
                   np.single(0.014285746031),
                   np.single(0.014484159648),
                   np.single(0.014682573266),
                   np.single(0.014880985953),
                   np.single(0.015079400502),
                   np.single(0.015277813189),
                   np.single(0.015476226807),
                   np.single(0.015674641356),
                   np.single(0.015873054042),
                   np.single(0.016071466729),
                   np.single(0.016269881278),
                   np.single(0.016468293965)
                   ]


def convertPath(path,length = 21):
    #Takes a length bit number and converts it into a length string of 0's and 1's
    pauses = str(bin(path))[2:]
    pauses = '0'*(length-len(pauses))+pauses
    return(pauses)

def constructBadelineRanges(path):
    #Takes a integer path and produces a set of ranges for what spinners get loaded
    ranges = []
    timeActive = np.single(0)
    pauses = convertPath(path,21)
    for i in range(21):
        dT = badelineThrowDT[i]
        if pauses[i]=='1':
            timeActive += dT * 10
            timeActive %=np.single(0.05)
        ranges.append([timeActive, timeActive + dT])
        timeActive += dT
        timeActive %=np.single(0.05)
    return(ranges)

def constructCustomRanges(path,slowdownAmounts):
    #Same as above, but allows custom ranges for custom slowdown.
    ranges = []
    timeActive = np.single(0)
    length = len(slowdownAmounts)
    pauses = convertPath(path,length)
    for i in range(length):
        dT = badelineThrowDT[i]
        if pauses[i]=='1':
            timeActive += dT * 10
            timeActive %=np.single(0.05)
        ranges.append([timeActive, timeActive + dT])
        timeActive += dT
        timeActive %=np.single(0.05)
    return(ranges)

def rangeViability(ranges):
    #Analyses a group of ranges for the potential to stun through them.
    bestNumbers = []
    maxInterval = 0
    for pair in ranges:
        for number in pair:
            number%=np.single(0.05)
            overlap = 0
            for i in range(len(ranges)):
                interval = ranges[i]
                if (number > interval[0] and number < interval[1]) or (number + np.single(0.05) < interval[1]):
                    overlap += 1
                    maxInterval = max(i,maxInterval)
                    break
            if overlap!=0:
                continue
            bestNumbers.append(number)
    bestNumbers.sort()
    return(bestNumbers,maxInterval)

def badelinePauseSequences():
    #Produces every pause sequence which allows you to stun through a badeline throw.
    i = 0
    allBest = []
    while i<2**21:
        i+=1
        z = rangeViability(constructBadelineRanges(i))
        if len(z[0])!=0:
            allBest.append([z[0],i])
        else:
            if z[1] < 19:
                amount = 2**(21 - z[1]-1)
          #  print(amount,i)
                i-=i%amount
                i+=amount
    return(allBest)

#Doesn't quite return below, but below is all the sequences
everyBadelineSequence = ['101001000111111111100', '101001100111111111100', '101001010111111111100', '100111110111111111100', '011111110111111111100', '101001000111111111110', '101001100111111111110', '101001010111111111110', '100111110111111111110', '011111110111111111110', '101001000111111111101', '101001100111111111101', '101001010111111111101', '100111110111111111101', '011111110111111111101', '101001000111111111111', '101001100111111111111', '101001010111111111111', '100111110111111111111', '011111110111111111111']

def slowdownPauseSequences(slowdownAmounts):
    #Produces every pause sequence which allows you to stun through this custom slowdown.
    i = 0
    allBest = []
    length = len(slowdownAmounts)
    while i<2**length:
        i+=1
        z = rangeViability(constructCustomRanges(i,slowdownAmounts))
        if len(z[0])!=0:
            allBest.append([z[0],i])
        else:
            if z[1] < length - 2:
                amount = 2**(length -z[1]-1)
                i-=i%amount
                i+=amount
    return(allBest)

def addFrames(timeActive,deltaTime,amount):
    #Adds multiple frames at a specific delta time.
    tA = timeActive
    for _ in range(amount):
        tA = addFrame(tA,deltaTime)
    return(tA)

def pause(timeActive,deltaTime):
    #Adds 10 frames at a specific delta time.
    return(addFrames(timeActive,deltaTime,10))

def addBadeline(timeActive):
    #from freeze frames
    global badelineThrowDT
    timeActive = addFrames(timeActive,badelineThrowDT[0],10)
    for rate in badelineThrowDT:
        timeActive = addFrame(timeActive,rate)
    return(timeActive)

def onInterval(timeActive, deltaTime, offset, interval = np.single(0.05)):
    #Simulates Celeste spinner loading with complete accuracy, as far as I know.
    lastFrame = math.floor((np.double(timeActive) - np.double(offset) - np.double(deltaTime))/np.double(interval))
    currentFrame = math.floor((np.double(timeActive) - np.double(offset))/np.double(interval))
    return(lastFrame < currentFrame)

def checkFrame(currentTA,offset,currentDT = np.single(0.016666699201),isPausing = False):
    #Checks if you will load a spinner this frame.
    if isPausing:
        currentTA = pause(currentTA,currentDT)
    currentTA = addFrame(currentTA,currentDT)
    return(onInterval(currentTA,currentDT,offset),currentTA)

def badelineThrow(pauseSequence,initialTA,offset,verbose = False):
    #Checks if this pause sequence with this time active and this offset will allow you to stun the badeline throw.
    global badelineThrowDT
    timeActive = initialTA
#    deltaTime = [np.single(0.016667) for _ in range(21)]
    deltaTime = badelineThrowDT
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
            print(', '.join([str(item) for item in [i, loadCheck,timeActive,(timeActive*60)%3]]))
    return(success)
