# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from zhihu.models import Answer
from scrapy.exceptions import DropItem
class BestzhihuPipeline(object):
    def process_item(self, item, spider):
        if item['vote']>=2000:
            try:
                answer = Answer.objects.get(question_link=item["question_link"])

                if not answer:
                    answer = Answer(**item)
                else:
                    answer.vote = item['vote']
                answer.save()

            except:
                answer = Answer(**item)
                answer.save()

            return item
        else:
            raise DropItem("Missing price in %s" % item)





