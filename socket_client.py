import sys
import socket
import selectors
import types
import pickle

import ManageBytes
import datetime

def start_connections(sel, host, port, num_conns, dict_tracker):
    # NOTE: modify how message is handled for multi-message
    message = dict_tracker['outb']

    server_addr = (host, port)
    connid = 1
    print("starting connection", connid, "to", server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE

    data = types.SimpleNamespace(
        connid=connid,
        msgout_total=len(message),
        msgin_total=-1,
        recv_total=0,
        message=message,
        outb=message,
        inb=b"",
    )

    sel.register(sock, events, data=data)


def service_connection(key, mask, sel, dict_tracker):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read

        if data.msgin_total == -1 and recv_data:
            # set the fixed header length
            data.msgin_total = ManageBytes.headerlen(recv_data)
            print("\nEVENT_READ: msgin_total = {}".format(data.msgin_total))

        print("\nEVENT_READ")
        if recv_data:
            data.recv_total += len(recv_data)
            data.inb += recv_data

            print("received", 
                    len(recv_data),
                    "and total recieved is {}".format(len(data.inb)),
                    "of {} bytes from connection".format(data.msgin_total),
                    data.connid)

            
        if not recv_data or data.recv_total == data.msgin_total:
            print("closing connection", data.connid, data.recv_total, data.msgin_total)
            sel.unregister(sock)
            sock.close()
            dict_tracker['inb'] = data.inb
            dict_tracker['response'] = ManageBytes.deserialize(data.inb)

    if mask & selectors.EVENT_WRITE:
        #if not data.outb and data.message:
        #    data.outb = data.messages.pop(0)
        if data.outb:
            #print("\nEVENT_WRITE")
            #print("sending", repr(data.outb), "to connection", data.connid)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]



def send(obj, host, port, num_conns=1):
    """ send obj to host/port
        NOTE: could be modified for multiple objcects
              and multiple connections.
    """
    dict_tracker = dict()
    dict_tracker['count'] = 1
    dict_tracker['outobj'] = obj
    dict_tracker['outb'] = ManageBytes.serialize(obj)

    sel = selectors.DefaultSelector()
        
    start_connections(sel, host, int(port), int(num_conns), dict_tracker)

    try:
        while True:
            events = sel.select(timeout=1)
            if events:
                for key, mask in events:
                    service_connection(key, mask, sel, dict_tracker)
            # Check for a socket being monitored to continue.
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        sel.close()

    return dict_tracker


def example():
    from Test import Test
    host = '127.0.0.1'  # Standard loopback interface address (localhost)
    port = 65432        # Port to listen on (non-privileged ports are > 1023)
    num_conns = 1

    dict_tracker = send(Test(msg=datetime.datetime.now()), host, port, num_conns)

    test = dict_tracker['response']
    test.show_additions()


#if len(sys.argv) != 4:
#    print("usage:", sys.argv[0], "<host> <port> <num_connections>")
#    sys.exit(1)

#host, port, num_conns = sys.argv[1:4]

