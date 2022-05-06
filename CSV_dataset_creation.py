import csv

def intialise():
    try:
        header = ['Category', 'Text']    
        with open('Scraping_cache.csv', 'w', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            file.close()
        return
    except FileExistsError:
        return

intialise()