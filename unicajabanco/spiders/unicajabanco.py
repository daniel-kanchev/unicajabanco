import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from unicajabanco.items import Article


class UnicajabancoSpider(scrapy.Spider):
    name = 'unicajabanco'
    start_urls = ['https://uniblog.unicajabanco.es/']

    def parse(self, response):
        categories = response.xpath('//div[@class="page-anchor-item"]//h2/a/@href').getall()
        yield from response.follow_all(categories, self.parse_category)

    def parse_category(self, response):
        links = response.xpath('//a[@class="link link-bbt"]/@onclick').getall()
        links = [link.split("'")[1].replace('\\', '').replace('u002D', '-') for link in links]
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('(//a[@class="flechas-pagination"])[last()]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse_category)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="date"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="text"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
