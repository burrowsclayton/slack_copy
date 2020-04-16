

import pickle

def serialize(obj, fixed_header_size=10):
    """ converts obj into a pickle, adds a fixed_header, 
        and then returns the byte-string
    """
    msg = pickle.dumps(obj)
    return bytes(f"{len(msg):<{fixed_header_size}}", 'utf-8')+msg

def headerlen(msg, fixed_header_size=10):
    """ extracts length of the byte string msg
        from the fixed header in msg.
    """
    return int(msg[:fixed_header_size]) + fixed_header_size

def deserialize(msg, fixed_header_size=10):
    """ deserialize the body of the byte string """
    return pickle.loads(msg[fixed_header_size:])

def readByteString(msg, sock, fixed_header_size=10):
    """ Takes a msg(byte string), sock(socket), and length
        fixed_header_size(int).  Reads the binary stream
        over the socket, de-pickles the object, and 
        returns the object
        
    """
    while True:
        full_msg = b''
        new_msg = True

        while True:
            msg = sock.recv(16)
            if new_msg:
                #print("new msg len:",msg[:HEADERSIZE])
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

            #print(f"full message length: {msglen}")

            full_msg += msg

            #print(len(full_msg))

            if len(full_msg)-HEADERSIZE == msglen:
                #print("full msg recvd")
                #print(full_msg[HEADERSIZE:])
                #print(pickle.loads(full_msg[HEADERSIZE:]))
                new_msg = True
                full_msg = b""

    obj = pickle.loads(full_msg)

    return obj

