import scrapy
import pymongo
import logging
import json
from toripchanger import TorIpChanger
import sys
from scrapy.crawler import CrawlerProcess


logging.basicConfig(filename="/home/kobayashi/Gitproject/spiderbro-lazi/Hoa/scrapy.log", filemode="w", level=logging.DEBUG)

ROOT_URL = "https://lazi.vn/"
ip_changer = TorIpChanger(tor_password='123123',
                          tor_port=9051, local_http_proxy='127.0.0.1:8118')


def setup_logger(logger_name, log_file, level=logging.INFO):

    log_setup = logging.getLogger(logger_name)
    formatter = logging.Formatter(
        '%(levelname)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    log_setup.setLevel(level)
    log_setup.addHandler(fileHandler)
    log_setup.addHandler(streamHandler)


def logger(msg, level, logfile):

    if logfile == 'one':
        log = logging.getLogger('log_one')
    if logfile == 'two':
        log = logging.getLogger('log_two')
    if level == 'info':
        log.info(msg)
    if level == 'warning':
        log.warning(msg)
    if level == 'error':
        log.error(msg)


setup_logger('log_one', "Hoa/db.log")


class Lazi_Toan_Spider(scrapy.Spider):
    name = "lazi_edu"

    myclient = pymongo.MongoClient(
        "mongodb://truongtd2:123123@42.113.207.170:27017")
    db = myclient["crawl"]
    collection = db["demo"]

    def __init__(self, category=None):
        self.failed_urls = []

    def insert_to_db(self, data):
        try:
            inserted_id = self.collection.update({"title": data["title"]}, data, upsert=True)
            logger('\t\tInsert data %s to DB successfully' + str(inserted_id), 'info', 'one')
        except:
            logger('\t\tFailed to insert data', 'info', 'one')

    def start_requests(self):
        urls = [
            "https://lazi.vn/edu/lists/hoa-hoc?start=1110"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        logger('Access ' + response.url, 'info', 'one')

        if response.status == 404:
            self.crawler.stats.inc_value('failed_url_count')
            self.failed_urls.append(response.url)

        # ==================
        changeip_success = False
        while changeip_success == False:
            try:
                ip_changer.get_new_ip()
                changeip_success = True
            except:
                changeip_success = False

        logging.info("Requesting %s" % response.url)
        for row in response.css('div.exercise_div h2 a::attr(href)').extract():
            access_success = False
            while access_success == False:
                try:
                    yield scrapy.Request(row, callback=self.one_subject, meta={"bindaddress": (ip_changer.get_current_ip(), 0)})
                    logger('\tTry access ' + row, 'info', 'one')
                    access_success = True
                    logger('\tAccess success', 'info', 'one')
                except:
                    access_success = False

        next_page = response.css(
            '#paging_box > div > div > ul > div:nth-child(4) > span > a::attr(href)').extract_first()

        if next_page is not None:
            next_page = ROOT_URL + next_page
            yield scrapy.Request(next_page, callback=self.parse)

    def one_subject(self, response):
        logging.info("\tRequesting %s" % response.url)
        title = response.css(
            'body > div.body_wrap > div > div.content > div.canh_phai > div.pro_content > div.article_title > h1::text').extract_first()
        questions = response.css(
            'body > div.body_wrap > div > div.content > div.canh_phai > div.pro_content > div.art_content').extract_first()
        answers = response.css(
            'body > div.body_wrap > div > div.content > div.canh_phai > div.pro_content > div.tra_loi_wrapper > div.tra_loi_content > div#filter_stage > div.ans_div > div.fill_all').extract()
        subject = response.css(
            '.edu_view_more_new > a:nth-child(2)::text').extract()
        classes = response.css(
            '.edu_view_more_new > a:nth-child(3)::text').extract()
        updated_time = response.css(
            "body > div.body_wrap > div > div.content > div.canh_phai > div.pro_content > div.create_date_in_list > table > tr:nth-child(2) > td::text").extract()

        data = {
            "title": title,
            "questions": questions,
            "answers": answers,
            "subject": subject,
            "classes": classes,
            "updated_time": updated_time
        }
        self.insert_to_db(data)

    def handle_spider_closed(self, spider, reason):
        self.crawler.stats.set_value(
            'failed_urls', ','.join(spider.failed_urls))
