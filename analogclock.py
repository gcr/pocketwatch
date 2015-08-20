#!/usr/bin/env python



from PyQt5.QtCore import QPoint, Qt, QTime, QTimer
from PyQt5.QtGui import QColor, QPainter, QPolygon
from PyQt5.QtWidgets import QApplication, QWidget, QToolBox

import ctypes
from ctypes import CFUNCTYPE, c_void_p, c_char_p, c_int, c_long
import ctypes.util

objc_lib = ctypes.cdll.LoadLibrary(ctypes.util.find_library('objc'))
id = c_void_p
sel = c_void_p

sel_registerName = CFUNCTYPE(sel, c_char_p)((b"sel_registerName", objc_lib))

window_sel = sel_registerName(b"window")
setCollectionBehavior_sel = sel_registerName(b"setCollectionBehavior:")
setLevel_sel = sel_registerName(b"setLevel:")
NSWindowCollectionBehaviorFullScreenPrimary = 128
NSWindowCollectionBehaviorCanJoinAllSpaces = 1 << 0
NSWindowCollectionBehaviorMoveToActiveSpace = 1 << 1
NSWindowCollectionBehaviorTransient = 1 << 3
NSWindowCollectionBehaviorStationary = 1 << 4
NSWindowCollectionBehaviorFullScreenAuxiliary = 1 << 8
ctypes.pythonapi.PyCObject_AsVoidPtr.restype = ctypes.c_void_p
ctypes.pythonapi.PyCObject_AsVoidPtr.argtypes = [ctypes.py_object]


send1 = CFUNCTYPE(id, id, sel)((b"objc_msgSend", objc_lib))
send2 = CFUNCTYPE(None, id, sel, c_long)((b"objc_msgSend", objc_lib))
PyCObject_AsVoidPtr = ctypes.PYFUNCTYPE(ctypes.c_void_p, ctypes.py_object)(
                          ('PyCObject_AsVoidPtr', ctypes.pythonapi))


def join_all_spaces(qtwin):
    """Create a full-screen button on qtwin.
    The window needs to be already shown.
    """
    view = qtwin.effectiveWinId()
    print(view)
    print(dir(view))
    print(view.ascobject())
    cocoawin = send1(PyCObject_AsVoidPtr(view.ascobject()), window_sel)
    import ctypes, objc
    _objc = ctypes.PyDLL(objc._objc.__file__)
    _objc.PyObjCObject_New.restype = ctypes.py_object
    _objc.PyObjCObject_New.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    def objc_object(id):
        return _objc.PyObjCObject_New(id, 0, 1)
    objc_object(cocoawin).setCollectionBehavior_(NSWindowCollectionBehaviorFullScreenAuxiliary |
                                                 NSWindowCollectionBehaviorCanJoinAllSpaces |
                                                 NSWindowCollectionBehaviorStationary)

    #print(cocoawin)
    #send2(cocoawin, setCollectionBehavior_sel,
    #      NSWindowCollectionBehaviorCanJoinAllSpaces |
    #      NSWindowCollectionBehaviorStationary |
    #      NSWindowCollectionBehaviorFullScreenAuxiliary
    #)
    #send2(cocoawin, setLevel_sel,
    #      10
    #)


class AnalogClock(QWidget):
    hourHand = QPolygon([
        QPoint(7, 8),
        QPoint(-7, 8),
        QPoint(0, -40)
    ])

    minuteHand = QPolygon([
        QPoint(7, 8),
        QPoint(-7, 8),
        QPoint(0, -70)
    ])

    hourColor = QColor(127, 0, 127)
    minuteColor = QColor(0, 127, 127, 191)

    def __init__(self, parent=None):
        super(AnalogClock, self).__init__(parent)

        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(1000)
        #timer = QTimer(self)
        #timer.timeout.connect(lambda: self.raise_())
        #timer.start(100)
        print(timer.isSingleShot())

        # Make this window an overlay.
        self.setAttribute(Qt.WA_TranslucentBackground |
                          Qt.WA_MacAlwaysShowToolWindow
                          )
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint |
                            Qt.Dialog
        )
        #self.setFloating(True)
        # Make visible on all spaces.

        self.setWindowTitle("Analog Clock")
        self.resize(200, 200)

    def paintEvent(self, event):
        side = min(self.width(), self.height())
        time = QTime.currentTime()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)

        painter.setPen(Qt.NoPen)
        painter.setBrush(AnalogClock.hourColor)

        painter.save()
        painter.rotate(30.0 * ((time.hour() + time.minute() / 60.0)))
        painter.drawConvexPolygon(AnalogClock.hourHand)
        painter.restore()

        painter.setPen(AnalogClock.hourColor)

        for i in range(12):
            painter.drawLine(88, 0, 96, 0)
            painter.rotate(30.0)

        painter.setPen(Qt.NoPen)
        painter.setBrush(AnalogClock.minuteColor)

        painter.save()
        painter.rotate(6.0 * (time.minute() + time.second() / 60.0))
        painter.drawConvexPolygon(AnalogClock.minuteHand)
        painter.restore()

        painter.setPen(AnalogClock.minuteColor)

        for j in range(60):
            if (j % 5) != 0:
                painter.drawLine(92, 0, 96, 0)
            painter.rotate(6.0)

    def mousePressEvent(self, event):
        self.close()


if __name__ == '__main__':

    import sys
    import AppKit
    info = AppKit.NSBundle.mainBundle().infoDictionary()
    info["LSBackgroundOnly"] = "1"

    app = QApplication(sys.argv)
    import AppKit
    # # https://developer.apple.com/library/mac/#documentation/AppKit/Reference/NSRunningApplication_Class/Reference/Reference.html
    # NSApplicationActivationPolicyRegular = 0
    # NSApplicationActivationPolicyAccessory = 1
    # NSApplicationActivationPolicyProhibited = 2
    # AppKit.NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    clock = None
    def show_clock():
        print("SHOWING CLOCK...")
        global clock
        clock = AnalogClock()
        clock.show()
        join_all_spaces(clock)
    show_clock()
    #timer = QTimer(app)
    #timer.timeout.connect(show_clock)
    #timer.start(3000)
    sys.exit(app.exec_())
