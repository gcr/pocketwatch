#!/usr/bin/env python

from PyQt5.QtCore import QObject, pyqtSignal, QTime, QTimer


class PomodoroControl(QObject):
    """A class that controls pomodoro working segments.

    Warning: May drift because no absolute times are used.
    """
    pomodoro_begin = pyqtSignal()
    pomodoro_complete = pyqtSignal()
    time_update = pyqtSignal([float, float])
    # signal: number of seconds elapsed, number of seconds remaining
    def __init__(self, parent=None):
        super(PomodoroControl, self).__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.handle_second)
        self.seconds_remaining = 0
        self.seconds_elapsed = 0

    @property
    def is_running(self):
        return self.timer.isActive()

    def start(self, seconds_remaining):
        self.seconds_remaining = seconds_remaining
        self.seconds_elapsed = 0
        self.timer.start(1000)
        self.pomodoro_begin.emit()
        self.time_update.emit(self.seconds_elapsed, self.seconds_remaining)

    def early_finish(self):
        self.timer.stop()
        self.pomodoro_complete.emit()

    def handle_second(self):
        self.seconds_elapsed += 1
        self.seconds_remaining -= 1
        self.time_update.emit(self.seconds_elapsed, self.seconds_remaining)
        if self.seconds_remaining == 0:
            self.timer.stop()
            self.pomodoro_complete.emit()


if __name__=="__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    ctl = PomodoroControl(app)
    def each_sec(i, j):
        print "Seconds left:",i
        print "Seconds elapsed:", j
    def begin():
        print "STARTING"
    def complete():
        print "STOPPING"
        ctl.start(5)
    ctl.pomodoro_begin.connect(begin)
    ctl.pomodoro_complete.connect(complete)
    ctl.time_update.connect(each_sec)

    ctl.start(10)

    app.exec_()
