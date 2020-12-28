import socket
import struct
import sys
import time

from pynput.keyboard import Key, Listener


team_name = b'Marcelo\n'
sock = None


def on_press(key):
    print('{0} pressed'.format(key))
    sock.sendall(team_name)


def on_release(key):
    print('{0} release'.format(key))
    if key == Key.esc:
        # Stop listener
        return False


def udp_recv_offer():
    client = socket.socket(socket.AF_INET,  # Internet
                           socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # Enable broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    print("Client started, listening for offer requests...")

    client.bind(("", 13117))
    data, addr = client.recvfrom(1024)  # buffer size is 1024 bytes
    if  data[:4] != bytes([0xfe, 0xed, 0xbe, 0xef]) or data[4] != 0x02:
        print("illegal format")
        return addr, -1
    port = struct.unpack('>H', data[5:7])[0]
    print("Received offer from %s, attempting to connect..." % addr[0])
    client.close()
    return addr, port


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
            print('client connected successfully, GO TEAM Marcelo!')
            data = sock.recv(1024)
            welcome_msg = data.decode("utf-8")
            print(welcome_msg)

            # Collect events until released
            with Listener(on_press=on_press) as listener:
                # listener.join()
                data = sock.recv(1024)
                listener.stop()
                print(repr(data))

            time.sleep(2)
            print("\n\n---------------\n\n")


if __name__ == "__main__":
    main(sys.argv[1:])

