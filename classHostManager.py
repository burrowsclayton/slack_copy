import random
import json, requests
import classUserAgent

class HostManager:
    """
    What does it do?  Randomly returns pre-approved host/port information
    for ProxyRotator service.
    """
    # Use Gateway from ProxyRotator.com
    # options.AddArguments("--proxy-server=http://user:password@yourProxyServer.com:8080")

    def __init__(self, header_dict=None, target_host='seekingalpha.com'):

        # ProxyRotator.com IP address (this is the proxy host)
        self.host = "199.189.86.111" 

        self.sticky_ports = dict({
            0 : (9501, 9750), # 0: sticky very fast US
            1 : (9801, 9900), # 1: sticky medium US
            2 : (10001, 10500), # 2: sticky medium Wolrd
            })

        self.random_ports = dict({
            0 : 9500, # 0: random very fast US
            1 : 9800, # 1: random medium US
            2 : 10000, # 2: random medium Wolrd
            })

        if header_dict == None:
            self.header_dict = {
                'Host': target_host,
                'Accept': 'text/html',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'DNT': '1',
                'Connection': 'close',
                'TE': 'Trailers'
                }
        else:
            self.header_dict = header_dict

        # a custom class of different, common user agents
        self.UserAgent = classUserAgent.UserAgent() 

    def getRequestHeaders(self):
        return self.UserAgent(self.header_dict)

    def getRandomHeader(self, proxy_rotator_header=False):
        if proxy_rotator_header == True:
            # Use this to get a random header 
            # NOTE: this doesn't seem to work well.  Instead
            #       just use the classUserAgent
            url = 'http://falcon.proxyrotator.com:51337/'

            params = dict(
                apiKey='PK6CjxFpmJfgosLVaRdDBYQS435A7ZNy'
            )

            resp = requests.get(url=url, params=params)
            return json.loads(resp.text)
        else:
            # This uses classUserAgent
            return self.UserAgent.get(self.header_dict)


    def getNextHost(self):
        sample_code = random.randint(1, 9)
        sample_code = 3

        if sample_code in [1, 5, 6]:
            port, meta = 9500, "very-fast; random"

        elif sample_code == 2:
            port, meta = 8081, "fast; random"

        elif sample_code == 3:
            port, meta = random.randint(9501, 9750), "very fast; sticky"

        else:
            port, meta = random.randint(9000, 9248), "fast; sticky"

        next_host = (self.host, int(port), meta, "{}:{}".format(self.host, int(port)))
        print("next host: {}:{}, {}".format(*next_host))
        return next_host
    
    def getProxyDict(self):
        # Use this is you want to manage the randomness yourself
        next_host = self.getNextHost()
        proxy_dict = {
                  "http" : "http://{}:{}".format(*next_host)
                , "https" : "http://{}:{}".format(*next_host)
                , "ftp" : "http://{}:{}".format(*next_host)
                }

        return proxy_dict

    def getRandomProxyDict(self, num=0):
        # Use this is you want ProxyRotator to manage the randomness
        port = self.random_ports[num]
        host = self.host 
        proxy_dict = {
                  "http" : "http://{}:{}".format(host, port)
                , "https" : "http://{}:{}".format(host, port)
                , "ftp" : "http://{}:{}".format(host, port)
                }
        return dict({
            'host' : host,
            'port' : port,
            'proxies' : proxy_dict,
            })


