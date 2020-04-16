
import classRequestManager
import socket_server_process as SSP
import ManageBytes

import os
import sys
import socket
import selectors
import types
import pickle
import datetime


if len(sys.argv) != 4:
    host = '127.0.0.1'  # Standard loopback interface address (localhost)
    port = 65432        # Port to listen on (non-privileged ports are > 1023)
    target_host = ''
    print("Missing CLI Args.", 
            "Default host: {}".format(host),
            "Default port: {}".format(port),
            "Default target_host: {}".format(target_host),
            )
else:
    host, port, target_host = sys.argv[1], int(sys.argv[2]), sys.argv[3]

sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(cnt=0, msglen=0, sent=0, addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask, SocketServerProcess):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)  # Should be ready to read
        
            if recv_data:
                data.outb += b''
                data.inb += recv_data

            #print(len(data.inb), int(data.inb[:10]))
        except:
            print("ErrorIn:", len(data.inb), "\n", data.inb[:10])

    if mask & selectors.EVENT_WRITE:
        # Process data before write back to client
        data.outb = SocketServerProcess.execute(data.inb)
        #data.outb = ManageBytes.serialize('hello from server')

        if data.outb and len(data.outb) > data.sent:
            #print("echoing", repr(data.cnt), repr(data.outb), "to", data.addr)
            def getDict(data):
                """ function for debugging """
                return {'datetime': datetime.datetime.now(),
                        'cnt':repr(data.cnt),
                        'msglen':data.msglen,
                        'data-sent':data.sent,
                        'data':len(data.outb),
                        }
                print(getDict(data)) # NOTE: DEBUG

            # Count the number of times we WRITE
            if data.cnt == 0:
                data.msglen = len(data.outb)
            data.cnt += 1

            try:
                data.sent = sock.send(data.outb)  # Should be ready to write
            except Exception as e:
                print("ErrorOut:\n", datetime.datetime.now(), "\n", e)
                print(data.outb[:10], "\n")
                sel.unregister(sock)
                sock.close()
                sel.close()
                quit()
            print(getDict(data))# NOTE: DEBUG
            data.outb = data.outb[data.sent:]

        else:
            print("closing connection to", data.addr)
            sel.unregister(sock)
            sock.close()


lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print("listening on", (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

con = None
cur = None
SocketServerProcess = SSP.SocketServerProcess(
        con,
        cur,
        target_host=target_host
        )
try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask, SocketServerProcess)
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
