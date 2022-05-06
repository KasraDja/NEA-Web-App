import json

def intialise():
    try:
        file = open('Scraping_cache.json', 'x') # creates the file if it doesn't exist, if it does throws an error.
        frame = {
            'post type': {
                'documentary':{
                    'url': [],
                    'title': [],
                    'synopsis': [],
                    'image': []
                    },
                'article':{
                    'url': [],
                    'title': [],
                    'synopsis': [],
                    'image': [] # do a stack
                    }, 
                'book':{
                    'url': [],
                    'title': [],
                    'synopsis': [],
                    'image': []
                    }
                }}
        return json.dump(frame, file, indent=4)#open('Scraping_cache.json', 'x').write(
    except FileExistsError:
        return
        
def savedata(data):
    file = open('C:/Users/Kasra Djadididan/OneDrive - Berkhamsted Schools Group/A-levels/Computer science/NEA/Scraping_cache.json', 'r')
    file_data = json.load(file)
    file.close()
    file_data['post type'][data[0]]['url'].append(data[1])
    file_data['post type'][data[0]]['title'].append(data[2])
    file_data['post type'][data[0]]['synopsis'].append(data[3])
    file_data['post type'][data[0]]['image'].append(data[4])
    file = open('C:/Users/Kasra Djadididan/OneDrive - Berkhamsted Schools Group/A-levels/Computer science/NEA/Scraping_cache.json', 'w+')
    return json.dump(file_data, file, indent=4) 
    
    #https://stackoverflow.com/questions/13949637/how-to-update-json-file-with-python

def addposttype(post_type):
    file = open('C:/Users/Kasra Djadididan/OneDrive - Berkhamsted Schools Group/A-levels/Computer science/NEA/Scraping_cache.json', 'r')
    file_data = json.load(file)
    file.close()
    post_type_frame = {post_type: { 'url': [],
                                    'title': [],
                                    'synopsis': [],
                                    'image': []
                                    }}
    file_data['post type'].update(post_type_frame)
    file = open('C:/Users/Kasra Djadididan/OneDrive - Berkhamsted Schools Group/A-levels/Computer science/NEA/Scraping_cache.json', 'w+')
    return json.dump(file_data, file, indent=4)



#intialise()