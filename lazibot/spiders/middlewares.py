import random

listproxy=[
	'http://139.255.92.26:53281',
	'http://195.123.219.193:3128',
	'http://45.235.87.65:60763',
	'http://152.204.128.46:50830',
	'http://1.20.98.168:37782',
	'http://188.246.106.182:48325',
	'http://1.20.98.168:37782',
	'http://152.204.128.46:50830'
]

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = random.choice(listproxy)
