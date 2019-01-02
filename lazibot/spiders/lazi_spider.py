import scrapy
import pymongo
import logging
import json

logging.basicConfig(filename="toDB.log", filemode="w", level=logging.DEBUG)

ROOT_URL = "https://lazi.vn/"


class LaziSpider(scrapy.Spider):
    name = "lazi"

    myclient = pymongo.MongoClient("mongodb://truongtd2:123123@42.113.207.170")
    db = myclient["crawl"]
    collection = db["web_crawl"]

    def insert_to_db(self, data):
        inserted_id = self.collection.insert_one(data)
        logging.debug('Insert data %s to DB successfully', inserted_id)
        return inserted_id

    def write_to_file(self, data):
        with open("/home/kobayashi/Gitproject/spiderbro-lazi/data.json", "a") as outfile:
            json.dump(data, outfile)

    def start_requests(self):
        urls = [
            "https://lazi.vn/edu/lists/toan-hoc"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for row in response.css('div.exercise_div h2 a::attr(href)').extract():
            yield scrapy.Request(row, callback=self.one_subject)
        next_page = response.css('#paging_box > div > div > ul > div:nth-child(4) > span > a::attr(href)').extract_first()
        if next_page is not None:
            next_page = ROOT_URL + next_page
            yield scrapy.Request(next_page, callback=self.parse)

    def one_subject(self, response):
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
        # self.write_to_file(data)
