import scrapy
import csv

TAG = ''

class Crawler(scrapy.Spider):
    name = 'dataset'
    start_urls = [
        #'https://theconversation.com/uk/topics/mathematics-98', #436 complete
        #'https://theconversation.com/uk/topics/physics-154', #322 complete
        #'https://theconversation.com/uk/topics/computer-science-6612', #72 complete
        #'https://theconversation.com/uk/topics/biology-521', #276 complete
        #'https://theconversation.com/uk/topics/chemistry-730', #251 complete
        #'https://theconversation.com/uk/topics/engineering-824', #174 complete
        #'https://theconversation.com/uk/topics/medicine-441' #225 complete
    ]

    def parse(self, response):
        data = []
        if 'Articles' in response.css('h1.legacy::text').get():
            Articles = response.css('h2 a::attr(href)').getall()
            nextpage = response.css('span.next a::attr(href)').get()
            global TAG
            TAG = response.css('title::text').get().split(' ', 1)[0]
            for i in Articles:
                yield response.follow(i, callback = self.parse)
            yield response.follow(nextpage, callback = self.parse)
        else:
            Content = textformater(response.css('div.grid-ten p::text').getall()).replace("\n", " ")
            data.extend((TAG, Content))
            savedata(data)
        

def savedata(data):
    with open('C:/Users/Kasra Djadididan/OneDrive - Berkhamsted Schools Group/A-levels/Computer science/NEA/Scraping_cache.csv', 'a', encoding = 'utf-8', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(data)
    return 

def textformater(list):
    text=''
    for i in list:
        text+= i
    return text
#https://news.mit.edu/topic/computers 