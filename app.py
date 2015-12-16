import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor, QPainter, QPolygon, QPen, QBrush, QPalette

from PomodoroControl import PomodoroControl
from PomodoroClockView import PomodoroClockView
app = QApplication(sys.argv)

ctl = PomodoroControl()
overlay = PomodoroClockView(ctl)
overlay.resize(150,150)
overlay.show()

def to_color(color):
    c = int(color, 16)
    return QColor(c >> 16 & 0xff,
                  c >> 8  & 0xff,
                  c       & 0xff)

def brighten(color):
    return QColor(int(color.red() * 0.75 + 64),
                  int(color.green() * 0.75 + 64),
                  int(color.blue() * 0.75 + 64))

# Experimenting with colors
# some good ones:
# http://www.colourlovers.com/palette/92095/Giant_Goldfish
# ???
# http://www.colourlovers.com/palette/577622/One_Sixty-Eight_%E2%98%86
# COLORS = [QColor(94,159,163),
#           QColor(220,209,180),
#           QColor(250,184,127),
#           QColor(248,126,123),
#           QColor(176,85,116),
#           ]
# http://www.colourlovers.com/palette/110225/Vintage_Modern
# I really, really like this one.
#COLORS = [QColor(140,35,24),
#            brighten(QColor(140,35,24)),
#          QColor(94,140,106),
#            brighten(QColor(94,140,106)),
#          QColor(136,166,94),
#            brighten(QColor(136,166,94)),
#          QColor(191,179,90),
#            brighten(QColor(191,179,90)),
#          #QColor(242,196,90),
#          ]
# Tomorrow theme, https://github.com/chriskempson/tomorrow-theme
COLORS = map(to_color, ["c82829",
                        "f5871f",
                        "eab700",
                        "718c00",
                        "3e999f",
                        "4271ae",
                        "8959a8",
                        "4d4d4c",
                        ])

# http://www.colourlovers.com/palette/845564/its_raining_love
# This one is also pretty good too.
# COLORS = [QColor(163, 169, 72),
#           QColor(237, 185, 46),
#           QColor(248, 89, 49),
#           QColor(206, 24, 54),
#           QColor(0, 153, 137),
#           ]
# http://www.colourlovers.com/palette/1811244/1001_Stories
# COLORS = [QColor(248,177,149),
#           QColor(246,114,128),
#           QColor(192,108,132),
#           QColor(108,91,123),
#           QColor(53,92,125),
#           # my own additions, mixing in Vintage Modern: :)
#           QColor(94,140,106),
#           QColor(136,166,94),
#           QColor(242,196,90),
#           ]
# http://www.colourlovers.com/palette/772970/200fruits_of_passion
# COLORS = [QColor(181,172,1),
#           QColor(236,186,9),
#           QColor(232,110,28),
#           QColor(212,30,69),
#           QColor(27,21,33),
#           ]
# http://www.colourlovers.com/palette/1283145/The_Way_You_Love_Me
# http://www.colourlovers.com/palette/692204/you_are_lovely._:*
# COLORS = [QColor(217,212,168),
#           QColor(209,92,87),
#           QColor(204,55,71),
#           QColor(92,55,75),
#           QColor(74,95,103),
#           ]
MINUTES = [25, 5, 25, 5, 25, 5, 25, 15]

def next_color():
    color = COLORS.pop(0)
    COLORS.append(color)
    overlay.set_color(color)
def next_pomodoro():
    time = MINUTES.pop(0)
    MINUTES.append(time)
    ctl.start(time * 60)

def make_printer(msg):
    def xx():
        print msg
    return xx

overlay.pomodoro_begin_requested.connect(make_printer("Begin requested"))
overlay.pomodoro_begin_requested.connect(next_pomodoro)
ctl.pomodoro_complete.connect(next_color)
overlay.pomodoro_pause_requested.connect(make_printer("Stop requested"))
overlay.pomodoro_pause_requested.connect(ctl.early_finish)

#next_pomodoro()
next_color()
app.exec_()
