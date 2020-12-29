import socket
import struct
import sys

from formats import PrintColors
from formats import getchar

team_name = b'Marcelo\n'
sock = None


# def on_press(key):
#     print('{0} pressed'.format(key))
#     key_str = str(key)
#     key_byte = key_str.encode("utf-8")
#     sock.sendall(key_byte)


# def on_release(key):
#     print('{0} release'.format(key))
#     if key == Key.esc:
#         # Stop listener
#         return False


def udp_recv_offer():
    client = socket.socket(socket.AF_INET,  # Internet
                           socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # Enable broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    print(PrintColors.OKGREEN + "Client started, listening for offer requests...")

    client.bind(("", 13117))
    data, addr = client.recvfrom(1024)  # buffer size is 1024 bytes
    if data[:4] != bytes([0xfe, 0xed, 0xbe, 0xef]) or data[4] != 0x02:
        print(PrintColors.RED + "illegal format")
        return addr, -1
    port = struct.unpack('>H', data[5:7])[0]
    print(PrintColors.OKGREEN + "Received offer from %s, attempting to connect..." % addr[0])
    client.close()
    return addr, port


def listen_to_keyPress():
    while True:
        ch = getchar()
        key_str = str(ch)
        key_byte = key_str.encode("utf-8")
        try:
            sock.sendall(key_byte)
        except:
            print("except: listen_to_keyPress")
            pass


def main(argv):
    main_loop = True
    while main_loop:
        addr_server, port_server = udp_recv_offer()

        HOST = addr_server[0]  # The server's hostname or IP address
        PORT = port_server

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            global sock
            sock = s
            sock.connect((HOST, PORT))
            sock.sendall(team_name)
            # data = sock.recv(1024)
            print(PrintColors.OKGREEN + 'client connected successfully, GO TEAM Marcelo!')
            data = sock.recv(1024)
            welcome_msg = data.decode("utf-8")
            print(PrintColors.OKCYAN + welcome_msg)

            # Collect events until released
            # with Listener(on_press=on_press) as listener:
                # listener.join()
                # data = sock.recv(1024)
                # listener.stop()

            t_keyboard = threads.Thread(name="t_keyboard", target=listen_to_keyPress)
            t_keyboard.start()
            # broadcast_thread.setDaemon(True)  # runs in the background without worrying about shutting it down.
            
            data = sock.recv(1024)
            t_keyboard.join()
            print(PrintColors.purple + "\n\n" + data.decode("utf-8"))

            print(PrintColors.purple + "=================\n")



if _name_ == "_main_":
    main(sys.argv[1:])