class HashTable():
    def __init__(self):
        self.primenumbers = [7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 
                            103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163 ,167, 173, 179, 181, 191, 193, 197, 
                            199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293]
        self.filename = 'ScrapedPostsHashtable'
        self.skip_factor = 3
        self.table = []
        with open(self.filename+'.txt', 'r', encoding='utf-8') as f: #opens the file that contains the hashtable inside, opens it so it can be edited 
            f.seek(0)                              #and creates if it doesnt exist and opens it interrepting it as text
            if len(f.readlines()) == 0:
                length = 5003
                self.table = ['' for i in range(length)]
            else:
                f.seek(0)
                for line in f:
                    stripped_line = line.strip()
                    if stripped_line == '':
                        self.table.append('')
                    else:
                        self.table.append(stripped_line)

    def insert(self,string):
        index = self.__value(string)
        flag = 0
        while self.table[index] != '' and flag<(len(self.table)/self.skip_factor): #collision
            index += self.skip_factor
            flag+=1
            index = index%len(self.table)
        if self.table[index] == '':
            self.table[index]= string
        else:
            self.__extend()
            self.insert(string)

    
    def find(self, string):
        index = self.__value(string)
        while self.table[index] != '':
            if string == self.table[index]:
                return True
            else:
                index += self.skip_factor
        return False

    def __extend(self):
        new_length = self.__nextprime((len(self.table)*2)-1)
        new_table = ['' for i in range(new_length)]
        temp = self.table
        self.table = new_table
        itertemp = iter(set(temp))
        next(itertemp)
        for i in itertemp:
            self.insert(i)
        
    def save(self):
        with open(self.filename+'.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.table))
            if self.table[-1]=='':
                f.write('\n')
            f.close()

    def __value(self, string):
        sum = 0
        length = len(string)
        for i, j in enumerate(string):
            sum += (ord(j))**(length+i) #I do to the power of the ordinal value of the chracter here as it will create the greatest change for the uniqueness of the charcaters in their positions in that order.
        return sum%len(self.table)      #as it will create the greatest change for the uniqueness of the charcaters in their positions in that order.

    def __nextprime(self, length):
        string = str(length)
        sum = 0
        root = length**0.5
        for i in string.split():
            sum+=int(i)
        if length%2 == 0 or length%5 == 0 or sum%3==0:
            length = self.__nextprime(length+1)
        elif not root%1==0:        
            for i in self.primenumbers:
                if length%i==0:
                    length = self.__nextprime(length+1)
                    break
        elif root is int:
            length = self.__nextprime(length+1)
        return length







table =  HashTable()
# #table.insert('george')
# if not table.find('jakey'):
#     table.insert('jakey')
# print(table.find('jakey'))
# #table.extend()
# table.save()
# for i in range(3000):
#     table.insert('george')
#     table.save()