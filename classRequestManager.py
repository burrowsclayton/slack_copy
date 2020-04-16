
import classHostManager
from datetime import datetime
import pickle
import sys

class RequestManager:
    """ Manages data to make requests as well as the results of the request.
        
        NOTE: target database must conform to insert statement in 
              the RequestManager.insert_to_database method.  Default
              table is 'Results', but this can be overwritten.
    """

    def __init__(self, link_dict, target_host, table_output="Links_Scraped"):
        """ HostManager is proxy and header source
            link_dict(dict): {'key':str, 'link':str}
            hm(HostManager): manages host and proxy information
            headers(dict): headers set by self.dict
            proxies(dict): proxies set by self.dict
            link_key(str): key of link to be scraped
            link(str): link to be scraped
            raw_html(binary-string): the html from link as binary-str
            html(str): the html from link as python string
            detla(float): seconds required to obtain raw_html
            status(int): 400 (error), 200 (all good), 0 (no attempt)
            resp(response): some sort of resposne from a request
            insert_stmnt(str): sql statement to insert results to SQLITE
        """
        self.link_dict = link_dict
        self.hm = classHostManager.HostManager(target_host=target_host)
        self.headers = dict()
        self.proxies = dict()
        self.key = link_dict['key']
        self.link = link_dict['link']
        self.raw_html = b''
        self.html = ''
        self.delta = -1
        self.status = 0
        self.resp = None

        self.table_output = table_output

        self.insert_stmnt = """
        insert or replace info {table}(
                key,
                headers,
                proxies,
                link,
                delta,
                size,
                status,
                insert_date
                ) values (
                ?--key,
                ?--headers,
                ?--proxies,
                ?--link,
                ?--delta,
                ?--size,
                ?--status,
                ?--insert_date)
        """.format(table=self.table_output)

    def set_config(self, config_dict):
        self.config_dict = config_dict
        self.num = self.config_dict['num']

    def get_dict(self):
        """ returns a dict of link, headers, and proxies """
        self.headers = self.hm.getRequestHeaders()
        self.proxies = self.hm.getRandomProxyDict(self.num)
        return {'link':self.link,
                'headers':headers,
                'proxies':proxies,
                't0':datetime.now(),
                't1':None,
                'response': None,}

    def set_dict(self, req_dict):
        """ Sets processes the contents of req_dict
            req_dict(dict): {
                'link':str, 'headers':str, 'proxies':str, 
                't0':datetime, 't1':datetime, 
                'response':response
                }
        """
        self.delta = (req_dict['t1'] - req_dict['t0']).total_seconds()
        resp = req_dict['response']

        if resp == None or resp.status==400:
            self.status = 400
        else:
            self.status = resp.status
            self.raw_html = resp.raw_html
            self.html = resp.html
            self.resp = resp 

    def pickle(self, base_path):
        """ base_path(str): path to write the pickle
        """
        d = {
                'key': self.key,
                'headers': self.headers,
                'proxies': self.proxies,
                'link': self.link,
                'delta': self.delta,
                'size': len(self.raw_html),
                'status': self.status,
                'date': datetime.now(),
                'raw_html': self.raw_html,
                }

        pickle.dumps(d, open('{}/{}.pkl'.format(base_path, self.key), 'wb'))

    def write_binary(self, base_path):
        """ base_path(str): path to write the html binary
        """
        # write html as a byte file
        path = '{}/{}.utf8binary'.format(base_path, self.key, encoding='utf-8')
        if self.raw_html != r'':
            with open(path, 'wb') as f:
                f.write(self.r.raw_html)

    def write_uft8(self, base_path):
        """ base_path(str): path to write the html binary
        """
        # write html as a html file
        path = '{}/{}.html'.format(base_path, self.key)

        if self.raw_html != r'':
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.r.html)

    def get_tup(self):
        """ A tuple of data from the scrape """

        tup = (
                self.key,
                self.headers,
                self.proxies,
                self.link,
                self.delta,
                self.size,
                self.status,
                datetime.now(),
            )
        return tup

    def insert_to_database(self, cur):
        """ cur(sqlite3.cursor): cursor to execute 
            table(str): target database table
        """
        cur.execute(self.insert_stmnt, self.get_tup())
