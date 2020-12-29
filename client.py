import socket
import struct
import sys
import time
from formats import PrintColors
from formats import getchar
from formats import PORT_BROAD
import threading as threads
import getch



team_name = b'Marcelo\n'
sock = None
can_send = False


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

    client.bind(("", PORT_BROAD))
    data, addr = client.recvfrom(1024)  # buffer size is 1024 bytes
    if data[:4] != bytes([0xfe, 0xed, 0xbe, 0xef]) or data[4] != 0x02:
        print(PrintColors.RED + "illegal format")
        return addr, -1
    port = struct.unpack('>H', data[5:7])[0]
    print(PrintColors.OKGREEN + "Received offer from %s, attempting to connect..." % addr[0])
    client.close()
    return addr, port


def listen_to_keyPress():
    global can_send
    timeout = time.time() + 10
    while 1:
        # ch = getchar()
        try:
            if can_send:
                # print("can send")
                ch = getch.getch()
                key_str = str(ch)
                key_byte = key_str.encode("utf-8")
                if can_send:
                    sock.sendall(key_byte)
        except:
            print("except: listen_to_keyPress")
            pass


def main():
    global can_send

    main_loop = True

    t_keyboard = threads.Thread(name="t_keyboard", target=listen_to_keyPress)
    t_keyboard.setDaemon(True)  # runs in the background without worrying about shutting it down.
    t_keyboard.start()

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
            can_send = True
            # Collect events until released
            # with Listener(on_press=on_press) as listener:
                # listener.join()
                # data = sock.recv(1024)
                # listener.stop()

            
            # listen_to_keyPress()
            # print("megia")
            data = sock.recv(1024)
            can_send = False
            # can_send = True
            # t_keyboard.join()
            print(PrintColors.purple + "\n\n" + data.decode("utf-8"))

            print(PrintColors.purple + "=================\n")



if __name__ == "__main__":
    main()