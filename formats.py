import sys
import termios
import tty

HOST = "10.0.2.15"
HOST_FORMAT = "10.0.2."
PORT_BROAD = 13117

class PrintColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\u001b[31m'
    Magenta = '\u001b[35'
    Yellow = '\u001b[33'
    purple = '\033[35m'
    RESET = '\u001b[0m'
    BackgroundBrightMagenta = '\u001b[45;1m'
    BackgroundBrightCyan = '\u001b[46;1m'


class BrodMSG(object):
    port: bytes
    magic_cookie = bytes([0xfe, 0xed, 0xbe, 0xef])
    type = bytes([0x02])

    def __init__(self, new_port):
        self.port = new_port

    def msg_to_bytes(self):
        return self.magic_cookie + self.type + self.port


def bytes_to_msg(msg_in_bytes):
    magic_cookie = msg_in_bytes[:4]
    type = msg_in_bytes[4]
    port = msg_in_bytes[5:7]
    return magic_cookie.decode("utf-8"), type.decode("utf-8"), port.decode("utf-8")


def getchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


# while 1:
#     ch = getchar()
#     print('You pressed', ch)