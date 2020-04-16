
import ManageBytes
import random
from datetime import datetime
import classRequestManager
import pickle

class SocketServerProcess:
    def __set(self, request_dict):
        """ Writes the contents of request_dict['arg'] 
            to a database.  

            request_dict(dict): a python dict
            request_dict['arg'](list(obj))
            
            The list contains a list of RequestManager
            objects from which we can get an 
            insert_stmnt(str) and a tuple.
            """

        def status_check(RequestManager):
            # NOTE: If you want to add more status checks,
            #       then do so here.
            """ Checks the status of links before we accept them.
                RequestManager(obj): a RequestManager object
            """
            bool1 = RequestManager.status == 200

            if bool1:
                return True
            else:
                return False

        def update_lists(RequestManager):
            """ Used to append link_dicts to link_scraped if we have
                a status that we are willing to accept.  It also
                adds a time stamp and updates self.link_log.

                RequestManager(obj): a RequestManager object

                If a link is accepted, then a few fields are
                added.  See __init__ for a description.
            """
            link_dict = RequestManager.link_dict

            if status_check(RequestManager):
                link_dict['insert_stmnt'] = RequestManager.insert_stmnt
                link_dict['tup'] = RequestManager.get_tup()
                self.link_scraped.append(link_dict)
            else:
                self.link_map.append(link_dict)

            def make_log(link_dict):
                link_dict['time'] = datetime.now()
                link_dict['insert_stmnt'] = """
                    insert into {log_table}(key, link, time)
                    values (?, ?, ?) """.format(self.log_table)

                link_dict['tup'] = (
                        link_dict['key'],
                        link_dict['link'],
                        link_dict['time'])

                self.link_log.append(link_dict)
        
        def wrapper(RequestManager_List):
            """ Creates a data_dict{'insert_stmn':str, 'rows':[tup]}
                and also updates self.link_map and self.link_scraped.

                RequestManager(list): a list of RequestManager objects
            """
            data_dict = {'insert_stmnt':"", 'rows':[]}
            
            for rm in RequestManager_List:
                data_dict['stmnt'] = rm.insert_stmnt
                data_dict['rows'].append(rm.get_tup())
                update_lists(rm)

            return data_dict

        RequestManager_List = request_dict['arg']

        data_dict = wrapper(RequestManager_List)

        self.cur.executemany(
                data_dict['insert_stmnt'],
                data_dict['rows'])

        self.con.commit()

    def __load(self):
        """ Loads the list of RequestManager objects. 
        """
        self.link_map = pickle.load(open("link_map.pkl", "rb"))

    def __load2(self):
        """ Loads the list of RequestManager objects """
        stmnt = """
            select page_key, formatted_link from {table1}
            where page_key not in (
                select 
                  key
                from {table2}
                )
        """.format(
                table1 = self.table1,
                table2 = self.table2)

        rows = self.cur.execute(stmnt).fetchall()

        random.shuffle(rows)

        def linkdict(row):
            """ RequestManager expects a dict of 
                {'key':str, 'link':str}. I designed 
                it this way so that arguements can be
                added, and the query rearranged, without causing 
                issues in the RequestManager object.
            """
            return {'key':row[0], 'link':row[1]}
        
        th = self.target_host
        rm = classRequestManager.RequestManager
        self.link_map = [rm(linkdict(row), th) for row in rows]
        pickle.dump(self.link_map, open("link_map.pkl", "wb"))

    def __unload(self):
        """ Unloads link_scraped and link_log to the Sqlite database
        """
        def unload(lst):
            insert_dict = dict()
            for link_dict in lst:
                try:
                    insert_dict[link_dict['insert_stmnt']].append(link_dict['tup'])
                except:
                    insert_dict[link_dict['insert_stmnt']] = link_dict['tup']

            for key in insert_dict.keys():
                insert_stmnt = key
                rows = insert_dict[key]
                try:
                    self.cur.executemany(insert_stmnt, rows)
                except Exception as e:
                    print(e)

        if len(self.link_scraped) == self.unload_cnt:
            unload(self.link_scraped)
            unload(self.link_log)
            

    def __get(self, request_dict):
        """ Process a request made by the the client 
            for request_dict['arg'] number of RequestManager
            objects.
        """
        rm = classRequestManager.RequestManager
        num_links = request_dict['arg']
        response_list = list()

        while len(response_list) != num_links:
            response_list.append(self.link_map.pop())
            
        print("List Length:", len(response_list), "\n")
        return response_list


    def __deserialize(self, data):
        """ Deserializes an pickled Python object """
        return ManageBytes.deserialize(data)

    def __serialize(self, response):
        """ Serializes an pickled Python object """
        byte_string = ManageBytes.serialize(response)
        print("\nMessage Length:", len(byte_string), "\n")
        return byte_string

    def __init__(self, con, cur, target_host, unload_cnt=100):

        """ con(sqlite.connection): connection to a db
            cur(sqlite3.cursor): cursor to execute 
            target_host: the target host used in 
                         the http request header.

            link_scraped([dict]): list of {'key':str, 'link':str, ...}
            link_map(RequestManager): list of RequestManager objects
            link_log([dict]): list of {'key':str, 'link':str, ...} 
        """
        self.con = con
        self.cur = cur
        self.target_host = target_host

        # NOTE: link_log and link_scraped will be flushed
        #       to SQLITE when len(link_scraped) == self.unload_cnt
        self.unload_cnt = 100

        self.table1 = 'Link_Map' 
        self.table2 = 'Link_Scraped'
        self.table_log = 'Link_Log'

        # link_map(list): [RequestManager]
        self.link_map = list()
        self.__load() # loads self.link_map
        #self.__load2() #NOTE: will eventually replace pickle load in self.__load()

        # link_scraped(list): 
        #   {'key':str, 'link':str, 'tup':tuple, 'insert_stmnt':str}
        self.link_scraped = list() 

        # link_log(list): 
        #   {'key':str, 'link':str, 'time':datetime, 'insert_stmnt':str}
        self.link_log = list()

        self.func_dict = {
                'set' : self.__set,
                'get' : self.__get,
                }

    def execute(self, bstr):
        """ Deserialize bstr(binary string) to get a dict called
            request_dict{'func':str, 'arg':obj}.

            Then execute the 'func' on 'arg' from the request_dict,
            and then return serialized output from func(arg).
        """
        #TODO: add some error handling here
        request_dict = self.__deserialize(bstr)
        print(request_dict)
        func_name = request_dict['func']

        func = self.func_dict[func_name]

        response = func(request_dict)

        return self.__serialize(response)

