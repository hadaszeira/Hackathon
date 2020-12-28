

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

