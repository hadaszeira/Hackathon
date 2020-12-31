import sys
import termios
import tty
import socket

HOST = socket.gethostbyname(socket.gethostname())
# HOST_FORMAT = "10.100.102."
# PORT_BROAD = 13117
# HOST = "172.1.0.4"
# HOST_FORMAT = "172.1.0."
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


good_job = """
   ____                 _        _       _     _
 / ____|               | |      | |     | |   | |
| |  __  ___   ___   __| |      | | ___ | |__ | |
| | |_ |/ _ \ / _ \ / _` |  _   | |/ _ \| '_ \| |
| |__| | (_) | (_) | (_| | | |__| | (_) | |_) |_|
 \_____|\___/ \___/ \__,_|  \____/ \___/|_.__/(_)"""


go_type = """
    ____         _______                      __
  / ____|       |__   __|                     \ \  
 | |  __  ___      | |_   _ _ __   ___    _____\ \ 
 | | |_ |/ _ \     | | | | | '_ \ / _ \  |______> >
 | |__| | (_) |    | | |_| | |_) |  __/        / / 
  \_____|\___/     |_|\__, | .__/ \___|       /_/  
                       __/ | |                     
                      |___/|_|                     """


go_get_your = """
                            _                             
                           | |                            
   __ _  ___      __ _  ___| |_    _   _  ___  _   _ _ __ 
  / _` |/ _ \    / _` |/ _ \ __|  | | | |/ _ \| | | | '__|
 | (_| | (_) |  | (_| |  __/ |_   | |_| | (_) | |_| | |   
  \__, |\___/    \__, |\___|\__|   \__, |\___/ \__,_|_|   
   __/ |          __/ |             __/ |                 
  |___/          |___/             |___/                  """


pizza2 = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣤⣶⣶⣦⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣷⣤⠀⠈⠙⢿⣿⣿⣿⣿⣿⣦⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣿⠆⠰⠶⠀⠘⢿⣿⣿⣿⣿⣿⣆⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣿⣿⠏⠀⢀⣠⣤⣤⣀⠙⣿⣿⣿⣿⣿⣷⡀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢠⠋⢈⣉⠉⣡⣤⢰⣿⣿⣿⣿⣿⣷⡈⢿⣿⣿⣿⣿⣷⡀
⠀⠀⠀⠀⠀⠀⠀⡴⢡⣾⣿⣿⣷⠋⠁⣿⣿⣿⣿⣿⣿⣿⠃⠀⡻⣿⣿⣿⣿⡇
⠀⠀⠀⠀⠀⢀⠜⠁⠸⣿⣿⣿⠟⠀⠀⠘⠿⣿⣿⣿⡿⠋⠰⠖⠱⣽⠟⠋⠉⡇
⠀⠀⠀⠀⡰⠉⠖⣀⠀⠀⢁⣀⠀⣴⣶⣦⠀⢴⡆⠀⠀⢀⣀⣀⣉⡽⠷⠶⠋⠀
⠀⠀⠀⡰⢡⣾⣿⣿⣿⡄⠛⠋⠘⣿⣿⡿⠀⠀⣐⣲⣤⣯⠞⠉⠁⠀⠀⠀⠀⠀
⠀⢀⠔⠁⣿⣿⣿⣿⣿⡟⠀⠀⠀⢀⣄⣀⡞⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⡜⠀⠀⠻⣿⣿⠿⣻⣥⣀⡀⢠⡟⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢰⠁⠀⡤⠖⠺⢶⡾⠃⠀⠈⠙⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⠓⠾⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""


pizza = """
                     ___              
                    |  ~~--.          
                    |%=@%%/           
                    |o%%%/            
                 __ |%%o/             
           _,--~~ | |(_/ ._           
        ,/'  m%%%%| |o/ /  `\.        
       /' m%%o(_)%| |/ /o%%m `\       
     /' %%@=%o%%%o|   /(_)o%%% `\     
    /  %o%%%%%=@%%|  /%%o%%@=%%  \    
   |  (_)%(_)%%o%%| /%%%=@(_)%%%  |   
   | %%o%%%%o%%%(_|/%o%%o%%%%o%%% |   
   | %%o%(_)%%%%%o%(_)%%%o%%o%o%% |   
   |  (_)%%=@%(_)%o%o%%(_)%o(_)%  |   
    \ ~%%o%%%%%o%o%=@%%o%%@%%o%~ /    
     \. ~o%%(_)%%%o%(_)%%(_)o~ ,/     
       \_ ~o%=@%(_)%o%%(_)%~ _/       
         `\_~~o%%%o%%%%%~~_/'         
            `--..____,,--'            
                                      """