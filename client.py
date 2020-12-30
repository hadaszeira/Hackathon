import socket
import struct
import time
from formats import PrintColors, PORT_BROAD, go_get_your, pizza
import threading as threads
import getch



team_name = b'Ohad_Golesh\n'
sock = None
can_send = False


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


def listen_to_key_press():
    global can_send
    timeout = time.time() + 10
    while 1:
        try:
            if can_send:
                # print("can send")
                ch = getch.getch()
                if ord(ch) == 3 or ord(ch) == 4:
                    break
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

    # start thread listening to key press
    t_keyboard = threads.Thread(name="t_keyboard", target=listen_to_key_press)
    t_keyboard.setDaemon(True)  # runs in the background without worrying about shutting it down.
    t_keyboard.start()

    while main_loop:
        addr_server, port_server = udp_recv_offer()

        # HOST = addr_server[0]  # The server's hostname or IP address
        
        HOST = "172.1.0.4"
        PORT = port_server
        print(HOST)
        print(PORT)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            global sock

            # Stage 2: connects in TCP to server and sends team name
            sock = s
            sock.connect((HOST, PORT))
            sock.sendall(team_name)
            print(PrintColors.OKGREEN + 'client connected successfully, GO TEAM!')

            # Stage 3: Waiting for Welcome msg and print it
            data = sock.recv(1024)
            welcome_msg = data.decode("utf-8")
            print(PrintColors.OKCYAN + welcome_msg)

            # Stage 4: Listening to keyboard press and send to server
            can_send = True
            data = sock.recv(1024)
            can_send = False

            # Stage 5: Game over, disconnected from curr server
            print(PrintColors.OKBLUE + data.decode("utf-8"))
            print(PrintColors.purple + "Server disconnected, listening for offer requests...")
            print(PrintColors.purple + "=================\n")
            print(go_get_your)
            print(pizza)
            print(PrintColors.purple + "=================\n")

if __name__ == "__main__":
    main()