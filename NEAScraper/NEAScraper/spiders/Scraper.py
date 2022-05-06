import scrapy
from scrapy.crawler import CrawlerProcess
import sys 
sys.path.append('C:/Users/Kasra Djadididan/OneDrive - Berkhamsted Schools Group/A-levels/Computer science/NEA')
import JSON_cache_editor as save
from HashTableClass import HashTable

class BookSpider(scrapy.Spider):
    name = 'WSBooks'
    start_urls = [
        'https://www.waterstones.com/category/science-technology-medicine/page/1'
        'https://www.waterstones.com/category/computing-internet?page=1',  
        'https://www.waterstones.com/category/popular-science-nature?page=1',
    ]
    def parse(self, response):
        data = []
        if response.css('div.search-results').get():# if search results page
            booklink = response.css('div.title-wrap a::attr(href)').getall()
            nextpage = response.css('a.next::attr(href)').get()
            for i in booklink:
                yield response.follow(i, callback = self.parse)
            yield response.follow(nextpage, callback = self.parse)
        else: #now a book
            table = HashTable()
            if  not table.find(booktitleformater(response.css('span.book-title::text').get())):
                data.append('book')
                bookurl = response.request.url #instead could have google search results to title or even an amazon affiliate link, to monetise this webapp
                booksynopsis = textformater(response.xpath('//div[@id="scope_book_description"]/p/text()').getall())
                #bookauthor = response.css('a.text-gold span::text').get()
                booktitle = booktitleformater(response.css('span.book-title::text').get())
                bookimage = response.css('div.book-image-main img::attr(src)').get()
                data.extend((bookurl, booktitle, booksynopsis, bookimage))
                SaveDataToCache(data)

def booktitleformater(Title):
    for i in range(len(Title)):
        if Title[i] == '(':
            Title = Title[:i]
            return Title

class CambridgeArticleSpider(scrapy.Spider):
    name = 'camarticles'
    start_urls = [
        'https://www.cam.ac.uk/latest-news'
    ]

    def parse(self, response):
        data = []
        try:
            if 'Latest news' in response.css('h1.cam-sub-title::text').get():
                Articles = response.css('div.view-content a::attr(href)').getall() #gets articles
                nextpage = response.css('li.pager-next a::attr(href)').get()#gets link to next page
                for i in Articles:
                    yield response.follow(i, callback = self.parse)
                yield response.follow(nextpage, callback = self.parse)
            else:
                table = HashTable()
                #print(response.css('h1.cam-sub-title::text').get())
                if not table.find(response.css('h1.cam-sub-title::text').get()):
                    data.append('article')
                    ArticleUrl = response.request.url
                    Title = response.css('h1.cam-sub-title::text').get()[1:].strip()
                    ArticleText = textformater(response.css('div.field-item p::text').getall())
                    Image = response.css('div.field-item img::attr(src)').get()
                    if Image != "https://i.creativecommons.org/l/by/4.0/88x31.png":
                        data.extend((ArticleUrl, Title, ArticleText, Image))
                        SaveDataToCache(data)
                    
        except TypeError:
            yield
        
def textformater(list):
    text=''
    for i in list:
        text+= i
    return text

class ConversationArticleSpider(scrapy.Spider):
    name = 'convarticles'
    start_urls = [
        'https://theconversation.com/uk/technology/articles',
        'https://theconversation.com/uk/environment/articles',
        'https://theconversation.com/uk/health/articles'
    ]

    def parse(self, response):
        data = []
        if response.css('h3.header::text').get():
            Articles = response.css('section.content-list h2 a::attr(href)').getall()
            nextpage = response.css('span.next a::attr(href)').get()
            for i in Articles:
                yield response.follow(i, callback = self.parse)
            yield response.follow(nextpage, callback = self.parse)
        else:
            table = HashTable()
            if not table.find(response.css('h1.entry-title strong::text').get()[1:].strip()):
                data.append('article')
                url = response.request.url
                Title = response.css('h1.entry-title strong::text').get()[1:].strip()
                Content = textformater(response.css('div.grid-ten p::text').getall())
                thumbnail = response.css('img.lazyloaded::attr(src)').get()
                data.extend((url, Title, Content, thumbnail))
                SaveDataToCache(data)

class DocumentarySpider(scrapy.Spider):
    name = 'documentaries'
    start_urls = [
        'https://documentaryheaven.com/category/educational/'
    ]

    def parse(self, response):
        data = []   
        if response.xpath('//*[@id="main"]/div[1]/h1/text()').get():
            documentaries = response.xpath('//div[1]/h2/a/@href').getall()
            nextpage = response.css('li.next-btn a::attr(href)').get()
            for i in documentaries:
                yield response.follow(i, callback = self.parse)
            yield response.follow(nextpage, callback = self.parse)
        else:
            table = HashTable()
            if not table.find(response.css('h1.entry-title::text').get()):
                data.append('documentary')
                url = response.request.url
                Title = response.css('h1.entry-title::text').get()
                Synopsis = textformater(response.css('div.entry-content p::text').getall())
                Thumbnail = response.xpath('//div[@id="video-preplay"]/img/@src').get()
                data.extend((url, Title, Synopsis, Thumbnail))
                SaveDataToCache(data)

class CourseSpider(scrapy.Spider):
    name = 'edx courses spider'
    start_urls = []
    
    def parse(self, response):
        yield

def SaveDataToCache(data):
    table = HashTable()
    table.insert(data[2])
    table.save()
    save.savedata(data)

def RunProcessScraping():
    process = CrawlerProcess()
    process.crawl(BookSpider)
    process.crawl(CambridgeArticleSpider)
    process.crawl(ConversationArticleSpider)
    process.crawl(DocumentarySpider)
    process.start()


process = CrawlerProcess()
process.crawl(BookSpider) #run this in a virtual environment
process.crawl(CambridgeArticleSpider)#done
process.crawl(ConversationArticleSpider)# done
process.crawl(DocumentarySpider) #done
process.start()