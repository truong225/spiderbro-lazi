




class ProxyMiddleware(object):

    def process_request(self, request, spider):
        request.meta['proxy'] = 'http://127.0.0.1:8118'
        spider.log('Proxy : %s' % request.meta['proxy'])


# from stem import Signal
# from stem.control import Controller


# def set_new_ip():
#     with Controller.from_port(port=9051) as controller:
#         controller.authenticate(password='123123')
#         controller.signal(Signal.NEWNYM)


# class ProxyMiddleware(object):
#     count = 0

#     def process_request(self, request, spider):
#         self.count += 1
#         if self.count == 100:
#             set_new_ip()
#             self.count = 0
#         request.meta['proxy'] = 'http://127.0.0.1:8118'
#         spider.log('Proxy : %s' % request.meta['proxy'])
