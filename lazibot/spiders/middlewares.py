import random

class ProxyMiddleware(object):
    listproxy=['http://139.255.92.26:53281', 'http://195.123.219.193:3128']
    def process_request(self, request, spider):
        request.meta['proxy'] = random.choice(listproxy)
