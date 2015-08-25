import sys
from PyQt5.QtWidgets import QApplication

from PomodoroControl import PomodoroControl
from PomodoroClockView import PomodoroClockView
app = QApplication(sys.argv)

ctl = PomodoroControl()
overlay = PomodoroClockView(ctl)
overlay.resize(150,150)
overlay.show()

ctl.start(60 * 15)

app.exec_()
