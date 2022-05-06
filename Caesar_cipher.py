KEY = 497
SYMBOLS = ''' !"#$%&\'()*+,-./:;<=>?@[]^_`{|}~'''

def encrypt(string):
    out = ''
    for i in range(len(string)):
        if string[i].isupper():#uppercase letter
            shift = KEY%26
            new = ord(string[i])+shift
            if new > 90:
                new = new-90+64
        elif string[i].islower():#lowercase letter
            shift = KEY%26
            new = ord(string[i])+shift
            if new > 122:
                new = new-122+96
        elif not string[i].isalnum(): #therefore a symbol
            shift = KEY%len(SYMBOLS)
            x = SYMBOLS.find(string[i]) + shift
            position = x%len(SYMBOLS)
            new = SYMBOLS[position] 
        else: #must be a number
            shift = KEY%10
            new = ord(string[i]) + shift
            if new > 57:
                new = new-57+47
        try:
            new = chr(new)
            out+=new
        except:
            out+=new
    return out


def decrypt(string): 
    out=''
    for i in range(len(string)):
        if string[i].isupper():#uppercase letter
            shift = KEY%26
            new = ord(string[i]) - shift
            if new < 65:
                new = new+90-64
        elif string[i].islower():#lowercase letter
            shift = KEY%26
            new = ord(string[i]) - shift
            if new < 97:
                new = new+122-96
        elif not string[i].isalnum(): #therefore a symbol
            shift = KEY%len(SYMBOLS)
            x = SYMBOLS.find(string[i]) - shift
            position = x%len(SYMBOLS)
            new = SYMBOLS[position]
        else: #must be a number
            shift = KEY%10
            new = ord(string[i]) - shift
            if new < 48:
                new = new+57-47
        try:
            new = chr(new)
            out+=new
        except:
            out+=new
    return out