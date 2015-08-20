#/usr/bin/env python

from PyQt5.QtCore import QPoint, Qt, QTime, QTimer
from PyQt5.QtGui import QColor, QPainter, QPolygon
from PyQt5.QtWidgets import QApplication, QWidget, QToolBox, QGraphicsView, QDialog

# import ctypes
# from ctypes import CFUNCTYPE, c_void_p, c_char_p, c_int, c_long
# import ctypes.util
import ctypes, objc

# Launch app in the background!
import sys
import AppKit
info = AppKit.NSBundle.mainBundle().infoDictionary()
info["LSBackgroundOnly"] = "1"
info["LSUIElement"] = "1"

class OverlayGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super(QGraphicsView, self).__init__(parent)
        # Make this window an overlay.
        self.setAttribute(#Qt.WA_TranslucentBackground |
                          Qt.WA_MacAlwaysShowToolWindow
                         )
        self.setWindowFlags(Qt.FramelessWindowHint |
                           Qt.WindowStaysOnTopHint |
                           Qt.Dialog
        )
    def show(self):
        super(QGraphicsView, self).show()

        # Constants
        NSWindowCollectionBehaviorFullScreenPrimary = 128
        NSWindowCollectionBehaviorCanJoinAllSpaces = 1 << 0
        NSWindowCollectionBehaviorMoveToActiveSpace = 1 << 1
        NSWindowCollectionBehaviorTransient = 1 << 3
        NSWindowCollectionBehaviorStationary = 1 << 4
        NSWindowCollectionBehaviorFullScreenAuxiliary = 1 << 8

        # Join all spaces (OSX-specific)
        ctypes.pythonapi.PyCObject_AsVoidPtr.restype = ctypes.c_void_p
        ctypes.pythonapi.PyCObject_AsVoidPtr.argtypes = [ctypes.py_object]
        cocoawin = objc.objc_object(c_void_p=
            ctypes.pythonapi.PyCObject_AsVoidPtr(
                self.effectiveWinId().ascobject()))
        cocoawin.window().setCollectionBehavior_(
            NSWindowCollectionBehaviorFullScreenAuxiliary |
            NSWindowCollectionBehaviorCanJoinAllSpaces |
            NSWindowCollectionBehaviorStationary
        )

if __name__=="__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)

    overlay = OverlayGraphicsView()
    overlay.resize(300,300)
    overlay.show()

    app.exec_()
