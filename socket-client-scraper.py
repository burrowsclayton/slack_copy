import classLinkClient
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
from classHostManager import HostManager
from datetime import datetime

def async_requests(RequestManagers):
    async def make_request(RequestManager, asession):
        rm_dict = RequestManager.dict()
        link = rm_dict['link']
        headers = rm_dict['headers']
        proxies = rm_dict['proxies']

        try:
            r = await asession.get(link, headers=headers, proxies=proxy_num)
            rm_dict['response'] = r
        except:
            pass

        rm_dict['t1'] = datetime.now()
        RequestManager.set_dict(rm_dict)
        return RequestManager

    r1, r2, r3, r4, r5, r6, r7, r8 = LinkClient.getLinks()
    asession = AsyncHTMLSession()

    async def get_link1():
        make_request(r1, assession)

    async def get_link2():
        make_request(r2, asession)

    async def get_link3():
        make_request(r3, asession)

    async def get_link4():
        make_request(r4, asession)

    async def get_link5():
        make_request(r5, asession)

    async def get_link6():
        make_request(r6, asession)

    async def get_link7():
        make_request(r7, asession)

    async def get_link8():
        make_request(r8, asession)

    return asession.run(get_link1, get_link2, get_link3, get_link4, get_link5,
            get_link6, get_link7, get_link8)

# TODO Setup proxy_num, link_num, host, and port for command line args
args = {
'proxy_num' : 1 ,
'link_num' : 1 ,
'host' : '127.0.0.1',  # Standard loopback interface address (localhost)
'port' : 65432,        # Port to listen on (non-privileged ports are > 1023)
}

LinkClient = classLinkClient.LinkClient(**args)
#LinkClient.load()
#LinkClient.show_links()
#quit()

while LinkClient.load() != False: # loop as long as there are pages to be downloaded
    #responses = asyncTrio(LinkClient) # execute scrapes
    #LinkClient.status() # display a status report
    #LinkClient.offload() # send results over socket
    LinkClient.show_links()

