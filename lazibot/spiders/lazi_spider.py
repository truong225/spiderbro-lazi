import scrapy


class LaziSpider(scrapy.Spider):
    name = "lazi"

    def start_requests(self):
        urls = [
            "https://lazi.vn/edu"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for row in response.css('div.exercise_div h2 a::attr(href)').extract():
            yield scrapy.Request(row, callback=self.one_subject)

    def one_subject(self, response):
        title = response.css('body > div.body_wrap > div > div.content > div.canh_phai > div.pro_content > div.article_title > h1::text').extract_first()
        subject = response.css('body > div.body_wrap > div > div.content > div.canh_phai > div.pro_content > div.art_content').extract_first()
        answers = 
