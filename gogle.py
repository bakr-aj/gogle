import nltk
import os
import pymysql
import glob
import re

class Gogle(object):
    def __init__(self):
        # Store all files in a variable called files
        print("Gogle is up and running")
        self.files = glob.glob("*.txt")

    def start_connection(self,host,port,user,password,db):
        self.conn = pymysql.connect(host=host,port=port,user=user,password=password,db=db)
        print("Successfully connected to the DB")


    # This function will read the files and extract the words and store them in uords
    def read_extract_words(self):
        print("Reading from the files")
        print(self.files);
        reg = re.compile('\W*')
        AllText  = ''
        for text in self.files:
            fi = open(text)
            AllText = fi.read()
            words = reg.split(AllText)
            self.calc_frequency(words,text)

        #SnowballStemmer = nltk.stem.snowball.SnowballStemmer("english")
    def calc_frequency(self,words,fileName):
        print("calculating the frequencies")
        dictionary = dict()
        lemma = nltk.wordnet.WordNetLemmatizer()
        pluralsStemmer = nltk.stem.porter.PorterStemmer()
        SnowballStemmer = nltk.stem.SnowballStemmer("english")
        for word in words:
            if len(word) > 0 :
                word = pluralsStemmer.stem_word(word)
                word = SnowballStemmer.stem(word)
                word = lemma.lemmatize(word)
                if (word in dictionary) and len(word) > 0:
                   dictionary[word] += 1
                else:
                   dictionary[word] = 1

        self.inserter(dictionary,fileName)


    def inserter(self,dictionary,fileName):
        print("inserting the word into the data base")
        cur = self.conn.cursor()
        sql = "INSERT INTO `indexer` (`word`,`frequency`,`fileName`) VALUES (%s , %s , %s)"

        for word,freq in dictionary.items():
            cur.execute(sql,(word,freq,fileName))

        self.conn.commit()


    def search(self,query):
        #this will return the words which we will search for
        searchReg = re.compile('and|or|not')
        queryWords = searchReg.split(query)
        conjuctionWords = searchReg.findall(query)
        querySteamedWords = []
        lemma = nltk.wordnet.WordNetLemmatizer()
        pluralsStemmer = nltk.stem.porter.PorterStemmer()
        SnowballStemmer = nltk.stem.SnowballStemmer("english")
        for word in queryWords:
            word = word.strip()
            if len(word) > 0 :
                word = pluralsStemmer.stem_word(word)
                word = SnowballStemmer.stem(word)
                word = lemma.lemmatize(word)
                querySteamedWords.append(word)

        print(querySteamedWords)
        if len(querySteamedWords) ==1:
            if len(conjuctionWords) >0:
                if conjuctionWords[0] =='not':
                    sql = "select fileName from indexer where word !=%s group by fileName order by  frequency desc"
                    cur = self.conn.cursor()
                    cur.execute(sql,(querySteamedWords[0]))
                    resl = cur.fetchall()
                    return resl;
            sql = "select fileName from indexer where word =%s group by fileName order by  frequency desc"
            cur = self.conn.cursor()
            cur.execute(sql,(querySteamedWords[0]))
            resl = cur.fetchall()
            return resl;
        elif len(querySteamedWords) == 2 :
            if len(conjuctionWords) >0:
                if conjuctionWords[0] == 'and':
                    sql="select a.fileName from (select fileName ,frequency from indexer where word=%s)as a join (select fileName,frequency from indexer where word=%s)as b on a.fileName = b.fileName group by fileName order by a.frequency desc;"
                    cur = self.conn.cursor()
                    cur.execute(sql,(querySteamedWords[0],querySteamedWords[1]))
                    resl = cur.fetchall()
                    return resl;
                elif conjuctionWords[0] == 'or':
                    sql = "select fileName,frequency from indexer where word=%s or word=%s group by fileName order by frequency desc;"
                    cur = self.conn.cursor()
                    cur.execute(sql,(querySteamedWords[0],querySteamedWords[1]))
                    resl = cur.fetchall()
                    return resl;
        else :
            return None

        #findall : will return the and or etc
        #thier a problem we encountered that we do not know where the boolean expr are so the word between

    def test(self):
        PROJECT_DIR=os.path.dirname(__file__)
        print(PROJECT_DIR)


    def indexing(self):
        print("Starting the indexing NOW")
        self.read_extract_words()

    files = None
    conn = None



gogle = Gogle()
gogle.start_connection("localhost",3306,"root","","gogle")
#gogle.indexing();
