import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6 import uic


classTitles = []
specifiedTimes = []
hwTitles = []
hwTimes = []
wakey = []
sleepy = []
timeVarT = False
chronList = []
overflowTime = 0

class ScheduleProgram(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ScheduleGUI.ui', self)
        self.setWindowTitle('import Calendar, print Productivity')
        self.setWindowIcon(QIcon('snakeIcon.ico'))

        global timeVarT
        timeVarT = False
        self.timeYes.clicked.connect(self.timeVar)
        self.submitButton.clicked.connect(self.submit)
        self.anotherYes.clicked.connect(self.anotherEvent)
        self.anotherNo.clicked.connect(self.runIt)

    def anotherEvent(self):
        self.eventName.setText('')
        self.startTime.setText('')
        self.endTime.setText('')
        self.estimatedTime.setText('')



    def runIt(self):
        global classTitles
        global specifiedTimes
        global hwTitles
        global hwTimes
        global wakey
        global sleepy
        global chronList
        chronList = self.makeSchedule()
        self.output.setText(self.printSchedule())

    def timeVar(self):
        global timeVarT
        timeVarT = True

    def submit(self):
        global classTitles
        global specifiedTimes
        global hwTitles
        global hwTimes
        global wakey
        global sleepy
        global timeVarT
        wakey.append(self.wakeTime.text())
        sleepy.append(self.sleepTime.text())
        startT = self.startTime.text()
        endT = self.endTime.text()
        if timeVarT:
            specifiedTimes.append([startT, endT])
            classTitles.append(self.eventName.text())
        else:
            hwTimes.append(self.estimatedTime.text())
            hwTitles.append(self.eventName.text())
        timeVarT = False

    def makeSchedule(self):
        global classTitles
        global specifiedTimes
        global hwTitles
        global hwTimes
        global wakey
        global sleepy
        global overflowTime

        wakeTime = wakey[0]
        sleepTime = sleepy[0]

        scheduledEvents = [] # [name, start, end]
        for i in range(len(classTitles)):
            scheduledEvents.append([classTitles[i], specifiedTimes[i][0], specifiedTimes[i][1]])

        # format start/end times into 24hr format and split into hr.fraction
        startTimes = []
        endTimes = []
        classBuffer = (15/2) #walk to class / bathroom break, divided by 2 to account for back to back classes being 15 min total apart

        for i in range(len(specifiedTimes)):
            # start time
            specifiedTimes[i][0] = specifiedTimes[i][0].split(":")
            specifiedTimes[i][0][1] = specifiedTimes[i][0][1].split(' ')
            if specifiedTimes[i][0][1][1] == 'pm':
                if int(specifiedTimes[i][0][0]) != 12:
                    specifiedTimes[i][0][0] = int(specifiedTimes[i][0][0]) + 12
            specifiedTimes[i][0][0] = int(specifiedTimes[i][0][0])
            specifiedTimes[i][0][0] += ((int(specifiedTimes[i][0][1][0]) - classBuffer) / 60)

            # end time
            specifiedTimes[i][1] = specifiedTimes[i][1].split(":")
            specifiedTimes[i][1][1] = specifiedTimes[i][1][1].split(' ')
            if specifiedTimes[i][1][1][1] == 'pm':
                if int(specifiedTimes[i][1][0]) != 12:
                    specifiedTimes[i][1][0] = int(specifiedTimes[i][1][0]) + 12
            specifiedTimes[i][1][0] = int(specifiedTimes[i][1][0])
            specifiedTimes[i][1][0] += ((int(specifiedTimes[i][1][1][0]) + classBuffer) / 60)

            specifiedTimes[i] = [float(specifiedTimes[i][0][0]), float(specifiedTimes[i][1][0])]
            startTimes.append(specifiedTimes[i][0])
            endTimes.append(specifiedTimes[i][1])


        # figure out free time
        startTimes.sort()
        endTimes.sort()
        eventLengths = []
        for i in range(len(startTimes)):
            eventLengths.append(endTimes[i] - startTimes[i])

        wakeTime = wakeTime.split(':')
        wakeTime[1] = wakeTime[1].split(' ')
        wakeHour = int(wakeTime[0])
        wakeMinFrac = int(int(wakeTime[1][0]) / 60)
        wakeUp = wakeHour + wakeMinFrac

        sleepTime = sleepTime.split(':')
        sleepTime[1] = sleepTime[1].split(' ')
        sleepHour = int(sleepTime[0]) + 12
        sleepMinFrac = int(int(sleepTime[1][0]) / 60)
        sleep = sleepHour + sleepMinFrac

    #     wakeUp = 7
    #     sleep = 23.999

        breakLengths = []
        breakLengths.append(startTimes[0] - wakeUp)

        for i in range(len(eventLengths) -1 ):
            breakLengths.append(startTimes[i+1] - endTimes[i])

        breakLengths.append(sleep - endTimes[-1])


        # figure out which break to do each assignment
        whenToDoThings = [] #[title, break indx, estimated length]
        enoughTime = True
        hwCount = 0

        longestBreakIndx = np.where(np.asarray(breakLengths) == max(breakLengths))[0][0]
        longestHWIndx = np.where(np.asarray(hwTimes) == max(hwTimes))[0][0]


        while hwCount < len(hwTitles) and enoughTime:
            enoughTime = not all(bl <= 0 for bl in breakLengths)
            if not enoughTime:
                overflow = sum(hwTimes)
                overflowTime = overflow
                return

            if float(breakLengths[longestBreakIndx]) >= float(hwTimes[longestHWIndx]):
                whenToDoThings.append([hwTitles[longestHWIndx], longestBreakIndx, float(hwTimes[longestHWIndx])])
                breakLengths[longestBreakIndx] -= float(hwTimes[longestHWIndx])
                hwTimes[longestHWIndx] = 0
                hwCount += 1

                longestBreakIndx = np.where(np.asarray(breakLengths) == max(breakLengths))[0][0]
                longestHWIndx = np.where(np.asarray(hwTimes) == max(hwTimes))[0][0]

            else:
                whenToDoThings.append([hwTitles[longestHWIndx], longestBreakIndx, breakLengths[longestBreakIndx]])
                hwTimes[longestHWIndx] = float(hwTimes[longestHWIndx]) - breakLengths[longestBreakIndx]
                breakLengths[longestBreakIndx] = 0

                longestBreakIndx = np.where(np.asarray(breakLengths) == max(breakLengths))[0][0]
                longestHWIndx = np.where(np.asarray(hwTimes) == max(hwTimes))[0][0]

        # figure out how many tasks we need to do in a given break
        tasks = {}
        totals = {}

        for task in whenToDoThings:
            indx = task[1]
            if indx in tasks:
                tasks[indx].append([task[0],task[2]])
                totals[indx] += task[2]
            else:
                tasks[indx] = [[task[0],task[2]]]
                totals[indx] = task[2]


        # figure out what time to start each task
        for i in totals.keys():
            try:
                hwStart = endTimes[i - 1]
            except:
                hwStart = wakeUp
            try:
                hwEnd = startTimes[i]
            except:
                hwEnd = sleep


            currentTime = hwStart
            for j in range(len(tasks[i])):
                this = [] # creating new event
                this.append(tasks[i][j][0]) # append name
                currentHour = 0
                currentMin = 0
                ampm = 'am'
                if currentTime >= 13:
                    ampm = 'pm'
                    tempTime = currentTime - 12
                    currentHour = int(tempTime)
                    currentMin = int((tempTime - int(tempTime)) * 60)
                else:
                    currentHour = int(currentTime)
                    currentMin = int((currentTime - int(currentTime)) * 60)

                if currentMin < 10:
                    currentMin = f'0{currentMin}'
                currentTimeStr = f'{currentHour}:{currentMin} {ampm}'

                this.append(currentTimeStr) # set start time

                currentTime = currentTime + float(tasks[i][j][1])
                currentHour = 0
                currentMin = 0
                ampm = 'am'
                if currentTime >= 13:
                    ampm = 'pm'
                    tempTime = currentTime - 12
                    currentHour = int(tempTime)
                    currentMin = int((tempTime - int(tempTime)) * 60)
                else:
                    currentHour = int(currentTime)
                    currentMin = int((currentTime - int(currentTime)) * 60)

                if currentMin < 10:
                    currentMin = f'0{currentMin}'
                currentTimeStr = f'{currentHour}:{currentMin} {ampm}'

                this.append(currentTimeStr)

                scheduledEvents.append(this)

                # add in scheduled 5 minute breaks if time allows
                if totals[i] + (5*(len(tasks[i])-1) / 60) < (hwEnd - hwStart):
                    currentTime += (5/60)

        # organize scheduled events into chronological order
        starts = {}
        for i in range(len(scheduledEvents)):
            s = scheduledEvents[i][1].split(":")
            hour = s[0]
            min = s[1].split(' ')[0]
            ampm = s[1].split(' ')[1]

            if ampm == 'pm' and int(hour) != 12:
                hour = int(hour) + 12

            minFrac = int(min)/60
            starts[float(hour) + minFrac] = i

        startTs = sorted(starts)
        chronologicalEvents = []
        wakeUpHour = int(wakeUp)
        wakeUpMin = int((wakeUp - int(wakeUp)) * 60)
        if wakeUpMin < 10:
            wakeUpMin = f'0{wakeUpMin}'
        wakeUpStr = f'{wakeUpHour}:{wakeUpMin} am'

        sleepHour = int(sleep) - 12
        sleepMin = int((sleep - int(sleep)) * 60)
        if sleepMin < 10:
            sleepMin = f'0{sleepMin}'
        ampm = 'pm'
        if sleepHour == 0:
            sleepHour = 12
            ampm = 'am'
        sleepStr = f'{sleepHour}:{sleepMin} {ampm}'

        chronologicalEvents.append(['wake up', wakeUpStr, wakeUpStr])
        for i in startTs:
            chronologicalEvents.append(scheduledEvents[starts[i]])
        chronologicalEvents.append(['go to bed', sleepStr, sleepStr])

        return chronologicalEvents

    def printSchedule(self):
        global chronList
        global overflowTime
        chronEvents = chronList
        returnString = ''
        try:
            for event in chronEvents:
                if event[0] == 'wake up':
                    returnString += f'Wake up! {event[1]}\n'
                elif event[0] == 'go to bed':
                    returnString += f'Bed time! {event[1]}'
                else:
                    returnString += f'{event[0]}: {event[1]} to {event[2]}\n'
        except:
            returnString += f"Not enough time in a day! Prioritize the tasks due soonest and rerun! Overflow: {overflowTime:0.2f} hours"

        return returnString


app = QApplication(sys.argv)

window = ScheduleProgram()
window.show()

try:
    sys.exit(app.exec())
except SystemExit:
    print('Closing Window...')
