from selenium import webdriver
from selenium.webdriver.common.by import By
from wordcloud import WordCloud
import time

#Simple web scraper app

# extracting data using a headless webdriver
# storing data for inspection
# using stored data for an application: visualization using word cloud


#Selenium based webdriver
options = webdriver.EdgeOptions()
options.add_argument('--headless')
#init driver using Edge
driver = webdriver.Edge(options=options)

#file to log all extracted sentences
filelogger = open("sentences.txt", "w", encoding="utf-16")

subreddit = 'brasil'

#URL to scrape
url = "https://www.reddit.com/r/"+subreddit
print(url)

#going to URL
start = time.time()
driver.get(url)
end = time.time()

print("time took: "+str(end-start)+" seconds")

#IMPORTANT: only works for reddit, any update to the page layout should break all signatures
#these signatures should return loaded reddit posts, but it's quite iffy
#TODO: generalize/refine all signatures
magic_path1 = ['/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[3]/div[1]/div[5]/div',\
               '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div[1]/div[4]/div',\
               '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[4]/div[1]/div[4]/div',\
               '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div/div[1]/div/div',\
               '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div/div/div/div/div']
index_path1 = 0

#trying second signature
if(len(driver.find_elements(By.XPATH,magic_path1[index_path1]))==0):
    index_path1 = 1

#trying third signature
if(len(driver.find_elements(By.XPATH,magic_path1[index_path1]))==0):
    index_path1 = 2
    
#trying fourth signature
if(len(driver.find_elements(By.XPATH,magic_path1[index_path1]))==0):
    index_path1 = 3
    
#trying fifth signature
if(len(driver.find_elements(By.XPATH,magic_path1[index_path1]))==0):
    index_path1 = 4


#this signature should obtain the title element from a post, somewhat consistent
magic_path2 = 'div/div/div[3]/div[2]/div'

#this should force the page to load most front page posts
#TODO: improve it somehow
driver.execute_script('window.scrollBy(0,2500)')
time.sleep(1)
driver.execute_script('window.scrollBy(0,2500)')
time.sleep(1)
driver.execute_script('window.scrollBy(0,2500)')
time.sleep(1)
driver.execute_script('window.scrollBy(0,2500)')
time.sleep(1)
driver.execute_script('window.scrollBy(0,2500)')
time.sleep(1)
driver.execute_script('window.scrollBy(0,2500)')
time.sleep(1)
driver.execute_script('window.scrollBy(0,2500)')
time.sleep(1)
driver.execute_script('window.scrollBy(0,2500)')
time.sleep(1)
driver.execute_script('window.scrollBy(0,2500)')
time.sleep(1)

num_titles = len(driver.find_elements(By.XPATH,magic_path1[index_path1]))
print('Titles obtained: ',num_titles)

#either the page was not loaded properly or all signatures failed to retrieve any post
if(num_titles == 0):
    filelogger.close()
    raise Exception('No posts, use a different signature')

#logging post titles to a file
for elm in driver.find_elements(By.XPATH,magic_path1[index_path1]):
    header_elm = elm.find_elements(By.XPATH,magic_path2)
    for h_elm in header_elm:
        filelogger.write(h_elm.get_attribute('innerText'))
        filelogger.write('\n')

#closing file
filelogger.close()

# application: word cloud

#retrieving all posts after extraction
filelogger = open("sentences.txt","r",encoding="utf-16")
wordtext = filelogger.read()

filelogger.seek(0)

start = time.time()
#filtering list
bwords = []

#bfile = open("verb3.txt","rt")
#verbs = bfile.read().splitlines()

#using NLP to filter unimportant words
import nltk

#experimenting with tags and automatic filters
tag_filter = ('VB','CC','CD','DT','EX','IN','JJ','LS','MD','PDT','POS','PR','RB','RP','TO','UH','W')
for line in filelogger.readlines():
	line = line.lower()
	structure = nltk.word_tokenize(line)
	tags = nltk.pos_tag(structure)
	for word in tags:
		if word[1].startswith(tag_filter):
			bwords.append(word[0])

#manual filters
pronounsverbs = ["I'm","you're","he's","she's","it's","we're","they're","I've"]

bwords.extend(pronounsverbs)

contractedverbs = ["aren't","isn't","didn't","don't","can't"]

bwords.extend(contractedverbs)

customwords = ["www","com","org","net"]

bwords.extend(customwords)

bwords = sorted(bwords)


#https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-whilst-preserving-order
def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

bwords = f7(bwords)


end = time.time()

print("finished creating filters(N="+str(len(bwords))+") in "+str((end-start))+" seconds")

#logging word filter for inspeciton
with open('filterlist.txt', 'w', encoding = "utf-16") as f:
    for item in bwords:
        f.write("%s\n" % item)
    f.close()

#generate wordcloud(filtered)
start = time.time()
wordcloud = WordCloud(max_font_size=185,width=1280,height=720,stopwords=bwords,collocations=False).generate(wordtext)
wordcloud.to_file(subreddit+".png")
end = time.time()
print("generated word cloud filtered in "+str(end-start)+" seconds")
#generate wordcloud(unfiltered)
start = time.time()
wordcloud = WordCloud(max_font_size=185,width=1280,height=720,collocations=False).generate(wordtext)
wordcloud.to_file(subreddit+"_unfiltered.png")
end = time.time()
print("generated word cloud "+str(end-start)+" seconds")
filelogger.close()