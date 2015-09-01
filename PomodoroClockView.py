#/usr/bin/env python
import math
from PyQt5.QtCore import (
    QEasingCurve,
    QPoint, Qt, QTime, QTimer, QPropertyAnimation, QRect, QRectF, QPointF,
    QState, QStateMachine,
    pyqtSignal, pyqtProperty,
    )
from PyQt5.QtGui import QColor, QPainter, QPolygon, QPen, QBrush, QPalette
from PyQt5.QtWidgets import QApplication, QWidget, QToolBox, QGraphicsView, QDialog, QGraphicsEllipseItem, QGraphicsScene, QGraphicsObject, QGraphicsDropShadowEffect

from OverlayGraphicsView import OverlayGraphicsView
from StateHelpers import make_state

class QColorThemedGraphicsObject(QGraphicsObject):
    """
    For all our graphics objects that need a color.
    """
    def get_color(self):
        return self._color
    def set_color(self,c):
        self._color = c
        self.update()
    color = pyqtProperty(QColor, get_color, set_color)


class ClockHandShape(QColorThemedGraphicsObject):
    """A single hand of a single clock. By default, this starts at 12
    O'Clock; use setRotation to change.
    Args: (x, y, length of the hand, width of the hand)
    """
    def __init__(self, x,y, sz, width=5, parent=None):
        super(ClockHandShape, self).__init__(parent)
        self.setPos(QPoint(x,y))
        self._sz = sz
        self._width = width
        self._color = QColor(0, 0, 0)
    def paint(self, painter, option, widget):
        #print(self.transformOrigin())
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(self._color,
                            self._width))
        painter.drawLine(0, self._sz*0.1,  0, -self._sz)
        W = self._width
        painter.setBrush(self._color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(-1.*W, -1.*W, 2.*W, 2.*W))
    def boundingRect(self):
        return QRectF(-2*self._width, -self._sz,
                      4*self._width, self._width+self._sz*1.1)

class SynchronizedClockHand(ClockHandShape):
    """
    This is a clock hand that automatically moves in time!
    """
    def __init__(self, mode, *args, **kw):
        super(SynchronizedClockHand,self).__init__(*args, **kw)
        self.mode = mode
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.handle_time_update)
        self.timer.start(1000)
        self.handle_time_update()
    def handle_time_update(self):
        time = QTime.currentTime()
        if self.mode == "hour":
            self.setRotation(time.hour() * 360. / 12.
                             + time.minute() * 360. / (60*12))
        elif self.mode == "minute":
            self.setRotation(time.minute() * 360. / 60.
                             + time.second() / 60. * 360. / 60.)
        elif self.mode == "second":
            self.setRotation(time.second() * 360. / 60.)

class ClockBack(QColorThemedGraphicsObject):
    """
    Draw a nice back face of the clock.
    This is just the white circle for now.
    """
    def get_alpha(self):
        return self._alpha
    def set_alpha(self,c):
        self._alpha = c
        self.update()
    alpha = pyqtProperty(float, get_alpha, set_alpha)
    def get_line_width(self):
        return self._line_width
    def set_line_width(self,c):
        self._line_width = c
        self.update()
    line_width = pyqtProperty(float, get_line_width, set_line_width)

    def __init__(self, size, *args, **kw):
        super(ClockBack,self).__init__(*args, **kw)
        self.size = size
        self.bbox = QRectF(0, 0, self.size, self.size)
        self._color = QColor(255,0,0,255)
        self._alpha = 255
        self._line_width = 3

    def paint(self, painter, option, widget):
        # Draw background
        painter.setPen(QPen(QColor(self._color.red(),
                                   self._color.green(),
                                   self._color.blue(),
                                   0.5*255 + 0.5*self._alpha
        ), self._line_width))
        # How much white to mix in?
        # At low alpha, I want the background to be super close to
        # pure white.
        A=(1 - 0.07*(self._alpha/255.))
        B=1-A
        painter.setBrush(QColor(255*A+B*self._color.red(),
                                255*A+B*self._color.green(),
                                255*A+B*self._color.blue(),
                                self._alpha
        ))
        center = self.size/2
        painter.drawEllipse(self.bbox)
        ## Draw four ticks along the sides
        #pen = QPen(QColor(self._color.red(),
        #                  self._color.green(),
        #                  self._color.blue(),
        #                  128), 2)
        #painter.setPen(pen)
        #START, END = 0.40, 0.43
        #painter.drawLine(QPointF(center, center + START*self.size),
        #                 QPointF(center, center + END*self.size))
        #painter.drawLine(QPointF(center, center - START*self.size),
        #                 QPointF(center, center - END*self.size))
        #painter.drawLine(QPointF(center + START*self.size, center),
        #                 QPointF(center + END*self.size, center))
        #painter.drawLine(QPointF(center - START*self.size, center),
        #                 QPointF(center - END*self.size, center))
    def boundingRect(self):
        return QRectF(-self._line_width,
                      -self._line_width,
                      self.size + 2*self.line_width,
                      self.size + 2*self.line_width)


class TimeElapsedView(QColorThemedGraphicsObject):
    """Draws the ever-updating "Time Elapsed" graph. This takes a starting
    time (in just minutes), an ending time (in just minutes), and will
    draw a constantly updating current time. The assumption is the
    ending time should be less than 60 minutes after starting time,
    and the current time should also be less than 60 minutes after
    starting.
    """
    def __init__(self, sz, thickness, pomodoro_control, parent=None):
        super(TimeElapsedView, self).__init__(parent)
        self._sz = sz
        self._thickness = thickness
        self._color = Qt.blue

        self._seconds_elapsed = 0
        self._seconds_remaining = 0

        # Recieve view updates from the Pomodoro Controller, horray~~
        self.pomodoro_control = pomodoro_control
        self.pomodoro_control.time_update.connect(self.update_time)

        # Must periodically repaint everything!
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def update_time(self, seconds_elapsed, seconds_remaining):
        self._seconds_elapsed = seconds_elapsed
        self._seconds_remaining = seconds_remaining
        print "time update: %d, %d"%(seconds_elapsed, seconds_remaining)
        self.update() # schedule repaint

    def boundingRect(self):
        return QRectF(-self._thickness,
                      -self._thickness,
                      self._sz + 2*self._thickness,
                      self._sz + 2*self._thickness)

    def paint(self, painter, option, widget):
        time = QTime.currentTime()
        minuteNow = time.minute() + (time.second() / 60.0)

        angleSecondsElapsed = 16*(360*self._seconds_elapsed / 60. / 60.)
        angleSecondsRemaining = 16*(360*self._seconds_remaining / 60. / 60.)
        thetaNow = 16*(90 - 360 * minuteNow / 60.)
        PADDING = 0.5*self._thickness

        # Time left
        painter.setPen(QPen(QColor(self._color.red(),
                                   self._color.green(),
                                   self._color.blue(),
                                   255),
                            self._thickness,
                            Qt.SolidLine,
                            #Qt.FlatCap if abs(theta3-thetaNow) < 16*20 else Qt.RoundCap,
                            Qt.FlatCap
                            #Qt.RoundCap
        ))
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(PADDING, PADDING,
                        self._sz-2*PADDING, self._sz-2*PADDING,
                        thetaNow, -angleSecondsRemaining)
        # Elapsed time
        painter.setPen(QPen(QColor(self._color.red(),
                                   self._color.green(),
                                   self._color.blue(),
                                   64),
                            self._thickness,
                            Qt.SolidLine,
                            Qt.FlatCap,
        ))
        painter.drawArc(PADDING, PADDING,
                        self._sz-2*PADDING, self._sz-2*PADDING,
                        thetaNow, angleSecondsElapsed)



class CircleObstruction(QColorThemedGraphicsObject):
    """
    Useful for notifications, I...guess?
    """
    def get_thickness(self):
        return self._thickness
    def set_thickness(self,c):
        self._thickness = c
        self.update()
    thickness = pyqtProperty(float, get_thickness, set_thickness)
    def __init__(self, sz, thickness, parent=None):
        super(CircleObstruction, self).__init__(parent)
        self._sz = sz
        self._thickness = thickness
        self._color = Qt.blue
    def boundingRect(self):
        return QRectF(-self._thickness,
                      -self._thickness,
                      self._sz + 2*self._thickness,
                      self._sz + 2*self._thickness)

    def paint(self, painter, option, widget):
        # painter.setPen(QPen(self._color,
        #                     self._thickness))
        painter.setBrush(self._color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(
            self._sz/2.0 - self._thickness,
            self._sz/2.0 - self._thickness,
            2*self._thickness,
            2*self._thickness,
        ))
    def show_anim(self):
        self.anim = QPropertyAnimation(self, "thickness")
        self.anim.setDuration(2000)
        self.anim.setStartValue(self.get_thickness())
        self.anim.setEndValue(50.0)
        self.anim.setEasingCurve(QEasingCurve.OutElastic)
        self.anim.start()
    def hide_anim(self):
        self.anim = QPropertyAnimation(self, "thickness")
        self.anim.setDuration(500)
        self.anim.setStartValue(self.get_thickness())
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.InBack)
        self.anim.start()




class PomodoroClockView(OverlayGraphicsView, QColorThemedGraphicsObject):
    pomodoro_begin_requested = pyqtSignal()
    pomodoro_pause_requested = pyqtSignal()

    def set_color(self, color):
        super(PomodoroClockView, self).set_color(color)
        self.hour_hand.set_color(self._color)
        self.minute_hand.set_color(self._color)
        self.clock_back.set_color(self._color)
        self.time_elapsed_view.set_color(self._color)
        self.obstruction.set_color(self._color)

    def __init__(self, pomodoro_control, parent=None):
        super(PomodoroClockView, self).__init__(parent)
        self.dragPosition = None
        self.pomodoro_control = pomodoro_control

        # Hide scrollbars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent")
        self.setRenderHint(QPainter.Antialiasing)

        # A scene containing all the parts of the clock
        scene = QGraphicsScene()
        self.setScene(scene)
        self.clock_back = ClockBack(100)
        self.hour_hand = SynchronizedClockHand("hour", 50, 50, 37*0.66, 2.3)
        self.minute_hand = SynchronizedClockHand("minute", 50, 50, 37, 2)
        self.time_elapsed_view = TimeElapsedView(100, 15, self.pomodoro_control)
        self.obstruction = CircleObstruction(100, 0)
        scene.addItem(self.clock_back)
        scene.addItem(self.hour_hand)
        scene.addItem(self.minute_hand)
        scene.addItem(self.time_elapsed_view)
        scene.addItem(self.obstruction)
        self.set_color(QColor(0,0,0))


        """
        Turns out I can't use a QStateMachine.
        Why?
        - I want this class to be *completely* subservient to the internal state
          of the PomodoroControl. When that changes its state, this class
          *reacts* to that change.
        - QStateMachine runs in its own event loop, which does not start until after
          the app's event loop runs. The state machine will refuse to catch signals
          until the app is already running. This means that *this class* must know
          whether it's starting at a started or stopped state.
        """
        self.pomodoro_control.pomodoro_begin.connect(self.pomodoro_begin)
        self.pomodoro_control.pomodoro_complete.connect(self.pomodoro_complete)
        if self.pomodoro_control.is_running:
            self.pomodoro_begin()
        else:
            self.pomodoro_complete()

    def pomodoro_begin(self):
        """
        Animation for beginning a pomodoro.
        """
        self.obstruction.hide_anim()
    def pomodoro_complete(self):
        """
        Animation for completing a pomodoro.
        """
        self.obstruction.show_anim()

        # def pp(x): print x
        # self.pomodoro_control.pomodoro_begin.connect(lambda: pp("Pomodoro is actually beginning."))
        # self.stopped_state.entered.connect(lambda: pp("STOPPED"))
        # self.running_state.entered.connect(lambda: pp("RUNNING"))

        # self.wait_for_start_state = QState()

        # self.wait_for_start_state.addTransition(self.pomodoro_control.pomodoro_begin,
        #                                         self.running_state)
        # self.running_state.addTransition(self.pomodoro_control.pomodoro_complete,
        #                                  self.wait_for_start_state)
        # self.wait_for_start_state.addTransition(
        #     self.mousePressEvent,
        #     self.pomodoro_begin_requested)
        # self.running_state.addTransition(
        #     self.mousePressEvent,
        #     self.pomodoro_pause_requested)

        #self.anim = QPropertyAnimation(self.obstruction, "thickness")
        #self.anim.setDuration(2000)
        #self.anim.setStartValue(0.0)
        #self.anim.setEndValue(50.0)
        #self.anim.setEasingCurve(QEasingCurve.OutElastic)
        #self.anim.start()
        #self.anim2 = QPropertyAnimation(self.clock_back, "line_width")
        #self.anim2.setDuration(1000)
        #self.anim2.setStartValue(1.0)
        #self.anim2.setEndValue(4.0)
        #self.anim2.setEasingCurve(QEasingCurve.OutExpo)
        #self.anim2.start()
        #self.anim3 = QPropertyAnimation(scene, "zoom")
        #self.anim3.setDuration(1000)
        #self.anim3.setStartValue(0.0)
        #self.anim3.setEndValue(1.0)
        #self.anim3.setEasingCurve(QEasingCurve.OutBounce)
        #self.anim3.start()


    def resizeEvent(self, evt):
        #super(PomodoroClockView, self).resize(w, h)
        w = evt.size().width()
        h = evt.size().height()
        # Transformation: let's let (50, 50) be the center and range from [0,100].
        self.fitInView(QRectF(-10, -10, 120, 120))
        self.setSceneRect(QRectF(0, 0, 100, 100))

    def mousePressEvent(self, evt):
        """
        Users can move the clock by dragging it aruond.
        """
        self.is_dragging = False
        if evt.button() == Qt.LeftButton:
            self.dragPosition = evt.globalPos() - self.frameGeometry().topLeft()
            evt.accept()
    def mouseMoveEvent(self, evt):
        self.is_dragging = True
        if Qt.LeftButton & evt.buttons():
            self.move(evt.globalPos() - self.dragPosition)
            evt.accept()
    def mouseReleaseEvent(self, evt):
        if not self.is_dragging:
            if self.pomodoro_control.is_running:
                self.pomodoro_pause_requested.emit()
            else:
                self.pomodoro_begin_requested.emit()
