#!/usr/bin/env python

from PyQt5.QtCore import QObject, pyqtSignal, QTime, QTimer


class PomodoroControl(QObject):
    pomodoro_begin = pyqtSignal()
    pomodoro_complete = pyqtSignal()
    each_second = pyqtSignal([int])
    def __init__(self, parent=None):
        super(QObject, self).__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.handle_second)
        self.seconds_remaining = 0

    @property
    def is_running(self):
        return self.timer.isActive()

    def start(self, seconds_remaining):
        self.seconds_remaining = seconds_remaining
        self.timer.start(1000)
        self.pomodoro_begin.emit()

    def handle_second(self):
        self.seconds_remaining -= 1
        self.each_second.emit(self.seconds_remaining)
        if self.seconds_remaining == 0:
            self.timer.stop()
            self.pomodoro_complete.emit()


if __name__=="__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    ctl = PomodoroControl(app)
    def each_sec(i):
        print "Seconds left: ",i
    def begin():
        print "STARTING"
    def complete():
        print "STOPPING"
        ctl.start(5)
    ctl.pomodoro_begin.connect(begin)
    ctl.pomodoro_complete.connect(complete)
    ctl.each_second.connect(each_sec)

    ctl.start(10)

    app.exec_()
