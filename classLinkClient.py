

import os
import ManageBytes
import socket_client
import classRequestManager

class LinkClient:
    """ NOTE: environment variable `ECS_CALLS` should be set
              as the destination for the HTML files to be saved.
    """
    def __init__(self, proxy_num, link_num, host, port):
        """ LinkeManager(int proxy_num, int link_num) 
            manages RequestManager objects
            and the interaction with server via socket.

            run_cnt(int): number of runs conducted by LinkClient
            proxy_num(int): index for classHostManager.HostManager
            link_num(int): the number of links to request from server
            host(str): host address to connect via socket
            port(int): host's port to connect via socket
            RequestManager_List(list): a list of RequestManager objects
        """
        self.run_cnt = -1 
        self.proxy_num = proxy_num
        self.link_num = link_num
        self.host = host
        self.port = port
        self.RequestManager_List= []

    def load(self, func='get', num_links=8):
        """ Loads self.RequestManager_List with requests a list of 
            RequestManager objects.
            arg(str): an arg to the server
        """
        req = {'func':func, 'arg':num_links}
        
        self.run_cnt += 1
        print("making request", self.run_cnt)

        dict_tracker = socket_client.send(
                req,
                self.host,
                self.port,
                )

        self.RequestManager_List = dict_tracker['response']

        if self.RequestManager_List and len(self.RequestManager_List) > 0:
            return True
        else:
            return False

    def offload(self, func='set'):
        """ Send self.RequestManager_List to back to the host
        """
        req = {'func':func, 'arg':self.RequestManager_List}

        dict_tracker = socket_client.send(
                req,
                self.host,
                self.port,
                )

    def status(self):
        """ Print out a count on number of links (good, bad)
        """
        cnt_good, cnt_bad = (0, 0)

        #TODO Alter how this is setup
        print(self.run_cnt)
        for req in self.RequestManager_List:
            print("\t", self.run_cnt, req.status, len(req.html))


    def write_utf8(self):
        """ write_utf8()
            Writes out the saved html as a html file
            to the path stored in the environemnt variable
            `ECS_CALLS`.
        """
        base_path = os.environ.get('ECS_CALLS')
        [rm.write_utf8(base_path) for rm in self.RequestManager_List]

    def write_binary(self):
        """ write_binary()
            Writes out the saved html as a binary html file
            to the path stored in the environemnt variable
            `ECS_CALLS`.
        """
        base_path = os.environ.get('ECS_CALLS')
        [rm.write_utf8(base_path) for rm in self.RequestManager_List]

    def show_links(self):
        """ A debug method to print out the link_dicts recieved
            from the server
        """
        print(self.run_cnt)
        [print(rm.link_dict['key']) for rm in self.RequestManager_List]
        print("\n")
