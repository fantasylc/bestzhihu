# -*- coding: utf-8 -*-
import re
import json
import time
from datetime import date
from scrapy import Spider,Request
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join,MapCompose
from scrapy.http import FormRequest
from bestzhihu.items import BestzhihuItem


class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['zhihu.com']
    start_urls = ['http://www.zhihu.com/node/ExploreAnswerListV2?params={%22offset%22:%200,%20%22type%22:%20%22day%22}']
    answers_list_xpath = "//div[@class='explore-feed feed-item']"

    question = ".//h2/a/text()"
    question_link = ".//h2/a/@href"

    # notice the space after zm-item-answser, Zhihu is naughty
    author = ".//div[@class='zm-item-answer ']/div[@class='answer-head']" + \
        "/div[@class='zm-item-answer-author-info']/a/text()"
    author_link = ".//div[@class='zm-item-answer ']" + \
        "/div[@class='zm-item-rich-text js-collapse-body']" + \
        "/div[@class='zh-summary summary clearfix']/a/@href"
    vote = ".//div[@class='zm-item-answer ']/div[@class='zm-item-vote']/a/@data-votecount"
    summary_img = ".//div[@class='zm-item-answer ']" + \
        "/div[@class='zm-item-rich-text js-collapse-body']" + \
        "/div[@class='zh-summary summary clearfix']/img"
    summary = ".//div[@class='zm-item-answer ']" + \
        "/div[@class='zm-item-rich-text js-collapse-body']" + \
        "/div[@class='zh-summary summary clearfix']/text()"
    answer = ".//div[@class='zm-item-answer ']" + \
        "/div[@class='zm-item-rich-text js-collapse-body']" + \
        "/textarea[@class='content hidden']/text()"

    item_fields = {
        "question": question,
        "question_link": question_link,
        "author": author,
        "author_link": author_link,
        "vote": vote,
        "summary_img": summary_img,
        "summary": summary,
        "answer": answer,
    }

    def parse(self, response):
        for when in ['day','month']:
            for offset in range(0,50,10):
                params = '"offset": {0}, "type": "{1}"'.format(offset, when)
                url = 'http://www.zhihu.com/node/ExploreAnswerListV2?params={' + params + '}'
                yield Request(url, callback=self.parse_answer)

    def parse_answer(self,response):
        selector = Selector(response)
        for answer in selector.xpath(self.answers_list_xpath):
            loader = ItemLoader(item=BestzhihuItem(), selector=answer)

            # define processors
            loader.default_input_processor = MapCompose(unicode.strip)
            loader.default_output_processor = Join()

            # iterate over fields and add xpaths to the loader
            for field, xpath in self.item_fields.iteritems():
                loader.add_xpath(field, xpath)

            item = loader.load_item()

            # convert the full text of answer into html
            m = item["answer"].encode('ascii', 'xmlcharrefreplace')
            item["answer"] = re.sub('width=\"\d+\"','width=100%',m)

            # if summary has image, convert it to html
            if "summary_img" in item:
                item["summary_img"] = item["summary_img"].encode('ascii', 'xmlcharrefreplace')
            else:
                item['summary_img'] = ""

            # change vote to integer
            item["vote"] = int(item["vote"])

            # in case of anonymous authors
            if "author" not in item:
                item["author"] = u'匿名用户'

            # complete links
            item["question_link"] = u"http://www.zhihu.com" + item["question_link"]

            if "author_link" in item:
                item["author_link"] = u"http://www.zhihu.com" + item["author_link"]
            else:
                item["author_link"] = ""

            # add the date when scraped
            item["date"] = date.today()

            yield item


