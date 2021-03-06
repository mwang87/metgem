import os
import sys

# Network visualisation
RADIUS = 30

# File format
FILE_EXTENSION = '.mnz'

try:
    path = os.path.join(sys._MEIPASS, 'LICENSE') if getattr(sys, 'frozen', False) else 'LICENSE'
    with open(path, 'r', encoding='UTF-8') as f:
        LICENSE_TEXT = "".join(f.readlines())
except (FileNotFoundError, IOError):
    LICENSE_TEXT = ""

DEBUG = False
EMBED_JUPYTER = False

if sys.platform.startswith('win'):
    USER_PATH = os.path.join(os.path.expandvars(r'%APPDATA%'), 'MetGem')
elif sys.platform.startswith('darwin'):
    USER_PATH = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'MetGem')
elif sys.platform.startswith('linux'):
    USER_PATH = os.path.join(os.path.expanduser('~'), '.config', 'MetGem')
else:
    USER_PATH = os.path.realpath('.')

DATABASES_PATH = os.path.join(USER_PATH, 'databases')
SQL_PATH = os.path.join(DATABASES_PATH, 'spectra.sqlite')
if sys.platform.startswith('darwin'):
    LOG_PATH = os.path.join(os.path.expanduser('~'), 'Library', 'Logs', 'MetGem')
else:
    LOG_PATH = os.path.join(USER_PATH, 'log')
STYLES_PATH = os.path.join(USER_PATH, 'styles')

if not os.path.exists(DATABASES_PATH):
    os.makedirs(DATABASES_PATH)

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

if not os.path.exists(STYLES_PATH):
    os.makedirs(STYLES_PATH)


def get_debug_flag() -> bool:
    return DEBUG


def set_debug_flag(val: bool):
    global DEBUG
    DEBUG = val


def get_jupyter_flag() -> bool:
    return EMBED_JUPYTER


def set_jupyter_flag(val: bool):
    global EMBED_JUPYTER
    EMBED_JUPYTER = val
