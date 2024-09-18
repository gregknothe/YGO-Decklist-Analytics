import pandas as pd
from urllib.request import Request, urlopen
import urllib.parse
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import random as rand
import time
import numpy as np


def decklistScrape(url):
    #scrapes the decklist from the URL and returns a dataframe with all cards and deck metadata
    req = requests.get(url, headers={'User-Agent': 'XYZ/3.0'}).text
    html = bs(req, features="lxml")

    #deck metadata
    deckID = url.split("-")[len(url.split("-"))-1]
    #print(html.find(class_="deck-metadata-info"))
    date = html.find(class_="deck-metadata-info").find_all("span")[len(html.find(class_="deck-metadata-info").find_all("span"))-1].get_text()
    date = date[1:].replace("st","").replace("nd","").replace("rd","").replace("th","")
    formatedDate = datetime.strptime(date, '%b %d %Y')

    test = html.find(class_="deck-metadata-container deck-bgimg").find_all("a")
    #test = html.find_all(class_="fa-solid fa-tag")
    #print(test)
    format = ""
    formatFlag = 0
    archetypeTags = []
    for x in range(len(test)):
        if formatFlag == 1:
            archetypeTags.append(test[x].get_text())
        #print(str(x) + ": " + str(test[x].get_text()))
        if test[x].get_text() == "Tournament Meta Decks":
            format = "TCG"
            formatFlag = 1
        elif test[x].get_text() == "Tournament Meta Decks OCG":
            format = "OCG"
            formatFlag = 1

    #individual card data
    nameList, typeList, deckList, codeList, imgSourceList, count = [], [], [], [], [], []
    for deckType in ["main_deck", "extra_deck", "side_deck"]:
        for tag in html.find_all(id=deckType):
            for tags in tag.find_all(class_="lazy"):
                nameList.append(tags.get("data-cardname"))
                typeList.append(tags.get("data-cardtype"))
                codeList.append(tags.get("data-name"))
                imgSourceList.append(tags.get("data-src"))
                deckList.append(deckType)
                count.append(1)
    df = pd.DataFrame({"name": nameList, "type": typeList, "deck": deckList, "code": codeList, "imgSource": imgSourceList, "count": count})
    df["deckID"], df["date"], df["format"], df["tags"] = deckID, formatedDate, format, "|".join(archetypeTags)
    return df

def getDeckURL(archetype, offset=0, limit=1000):
    #Gets all tournament top cut decks from specified archetype
    url = "https://ygoprodeck.com/api/decks/getDecks.php?tournament=tier-2&_sft_post_tag="+ archetype + "&offset=" + str(offset) + "&limit=" + str(limit)
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    webpage = urlopen(req, timeout=10).read()
    html = str(bs(webpage, features="lxml"))
    deckURLs = html.split('"pretty_url":"')
    for x in range(len(deckURLs)):
        deckURLs[x] = deckURLs[x].split('"')[0]
    deckURLs.pop(0)
    return deckURLs

def getURLs(archetype, limit=1000):
    #Gets all deck urls from search results. Does round up limit to the nearest 20s to make it easier.
    urlList = []
    for x in range(round(limit/20)+1):
        try:
            urlList.append(getDeckURL(archetype, offset=(x*20), limit=limit))
        except:
            break
    allurls = [j for i in urlList for j in i]
    return allurls

#print(getURLs("Spright"))

"""
#Testing single deck scraping
#url = "https://ygoprodeck.com/deck/branded-despia-520607"
url = "https://ygoprodeck.com/deck/fiendsmith-azamina-snake-eye-524591"
print(decklistScrape(url))
"""

"""
#Test to see if the decklist url scrape is working
#print(len(getURLs("snake-eye", limit=10000)))
#print(len(getURLs("mikanko", limit=10000)))
"""

archetypeList = ["snake-eye", "fire%20king", "tenpai%20dragon", "rescue-ace", "despia", "kashtira", "voiceless%20voice", "unchained", "tearlaments", 
                 "purrely", "labrynth", "mannadium", "floowandereeze", "chimera", "runick", "yubel", "dragon%20link", "centur-ion", 
                 "spright", "vanquish%20soul", "melodious", "salamangreat", "infernoble%20knight", "rikka", "orcust", "horus", "ritual%20beast", 
                 "rikka", "mikanko", "marincess", "swordsoul", "fur%20hire", "phantom%20knights", "scareclaw", "dark%20world", 
                 "mathmech", "dinomorphia", "drytron", "tri-brigade", "virtual%20world", "synchron", "volcanic", "plunder%20patroll", "white%20forest", 
                 "raidraptor", "memento", "traptrix", "gimmick%20puppet", "blackwing", "sky%20striker", "exosister", 
                 "infernoid", "lightsworn", "shark", "ghoti", "machina", "infinitrack", "train", "superheavy%20samurai", "eldlich", "goblin", "altergeist", 
                 "stardust", "@ignister", "thunder%20dragon", "bystial", "phantom%20knights", "paleozoic", "spellbook", "t.g.", "ogdoadic", 
                 "abyss%20actor", "world%20chalice", "gold%20pride", "p.u.n.k.", "resonator", "generaider", "mimighoul", "magical%20musket", "vaalmonica", 
                 "fluffal", "shining%20sarcophagus", "dark%20magician", "destruction%20sword", "evil%20eye", "egyptian%20god", "naturia",
                 "kozmo", "danger!", "crystal%20beast", "ninja", "earthbound", "zoodiac", "shaddoll", "resonator", "speedroid", "invoked", 
                 "magician", "gravekeeper's", "dracoslayer", "therion", "machina", "cyber%20dragon", "dogmatika", 
                 "code%20talker", "abc", "karakuri", "tellarknight", "vernusylph", "galaxy", "aroma", "ragnaraika", "elemental%20hero", "destiny%20hero", "vision%20hero",
                 ]

"""
def updateArcheTypeURLs():
    for archetype in archetypeList:

        currList = getURLs(archetype, limit=20)
        if len(currList) == 0:
            print("----------------------->" + archetype + "<--------------------------------")
        else:
            print(archetype)
    return

updateArcheTypeURLs()
"""

### archetypeURL.append(urllib.parse.quote(archetypes[x])) turns archetype into url

def getArchetypes():
    #Fetches all archetype tags
    url = "https://ygoprodeck.com/category/deck-archetypes/"
    req = requests.get(url, headers={'User-Agent': 'XYZ/3.0'}).text
    html = bs(req, features="lxml")
    archetypes = html.find_all(class_="deck-layout-single-flex")
    archetypeURL = []
    for x in range(len(archetypes)):
        archetypes[x] = archetypes[x].get_text().replace(" Decks", "").replace("\n", " ")
        # 'Mayakashi\nShiranui' might come up as a problem later, keep an eye on it
        #archetypeURL.append(urllib.parse.quote(archetypes[x]))
    #df = pd.DataFrame({"archetype": archetypes, "archetypeURL": archetypeURL})
    #df["lastestDeck"] = 0
    #df.to_csv("archetypes.csv",sep="|")
    return archetypes

def parseArchetypes(archetypeList: list):
    #Converts list of archetypes to usable URL strings
    archetypeURL = []
    for x in range(len(archetypeList)):
        archetypeURL.append(urllib.parse.quote(archetypeList[x]))
    return archetypeURL

def createArchetypeFile():
    #Creates a fresh archetype file with variables: 
    #   archetype: the name of the archetype
    #   archetypeURL: the parsed version of the name 
    #   lastDeck: deck ID of last deck added to archetyhpe
    arch = getArchetypes()
    archURL = parseArchetypes(arch)
    df = pd.DataFrame({"archetype": arch, "archetypeURL": archURL})
    df["lastDeck"] = 0
    df["deckCount"] = 0
    df.to_csv("archetypes.csv",sep="|", index=False)
    return df

def updateArchetypeFile():
    #Adds new archetypes to the bottom of the archetypes.csv
    newArchList = getArchetypes()
    oldArch = pd.read_csv("archetypes.csv", sep="|")
    oldArchList = list(oldArch["archetype"])
    newArchetypes = [x for x in newArchList if x not in oldArchList]
    newArchetypesURL = parseArchetypes(newArchetypes)

    if len(newArchetypes) >= 1:
        for x in range(len(newArchetypes)):
            print(f"--Adding new archetype: {newArchetypes[x]}")
            newRow = {"archetype": newArchetypes[x], "archetypeURL": newArchetypesURL[x], "lastDeck": 0}
            oldArch.loc[len(oldArch)] = newRow
        print(oldArch)
        oldArch.to_csv("archetypes.csv",sep="|", index=False)
    else:
        print("--No new archetypes added.")
    return oldArch

#updateArchetypeFile()

#print(getURLs("Jinzo"))

def createDeckListFile():
    #Scrapes every single deck list possible for all archetypes
    #arch = updateArchetypeFile()
    arch = pd.read_csv("testtypes.csv", sep="|")
    archList = list(arch["archetypeURL"])
    urlList = []
    newestURL, deckCount = [], []
    pop = 1

    for currType in archList:
        currList = getURLs(currType)
        if len(currList) == 0:
            print(str(pop) + " -0: " + str(currType))
            newestURL.append(0)
            deckCount.append(0)
        else:
            print(str(pop) + " +" + str(len(currList)) + ": " +  str(currType))
            urlList.extend(currList)
            newestURL.append(np.char.rpartition(currList[0], "-")[2])
            deckCount.append(len(currList))
            #res = np.char.rpartition(test_string, ', ')
        pop += 1 
        time.sleep(1)

    df = pd.DataFrame({'url': urlList})
    df.to_csv('testlist.csv', index=False)
    arch["lastDeck"] = newestURL
    arch["count"] = deckCount
    arch.to_csv("testtypes.csv", sep='|', index=False)
    return

#Find a way to update the old archetype file when pulling new data
#updateDataFrame()

#print(getURLs("tearlaments"))

#createDeckListFile()

#createArchetypeFile()
#print("done")

def uniqueURLs():
    arch = pd.read_csv("list.csv", sep="|")
    uniqueURL = arch['url'].unique()
    df = pd.DataFrame({'url': uniqueURL})
    df.to_csv("uniqueURL.csv", sep='|', index=False)
    return

#uniqueURLs()

"""
def dsgfsdfsdf(limit=1000):
    #Gets all tournament top cut decks from specified archetype
    url = "https://ygoprodeck.com/deck-search/?tournament=tier-2&offset=0"
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    webpage = urlopen(req, timeout=10).read()
    html = str(bs(webpage, features="lxml"))
    deckURLs = html.split('"pretty_url":"')
    for x in range(len(deckURLs)):
        deckURLs[x] = deckURLs[x].split('"')[0]
    deckURLs.pop(0)
    df = pd.DataFrame({'url': deckURLs})
    df.to_csv("uniqueURL2.csv", sep='|', index=False)
    return 

#dsgfsdfsdf()
"""

def getPageURL(offset=0, limit=20000):
    #Creates list with URL for each decklist on page.
    url = "https://ygoprodeck.com/api/decks/getDecks.php?tournament=tier-2&offset=" + str(offset) + "&limit=" + str(limit)
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    webpage = urlopen(req, timeout=10).read()
    html = str(bs(webpage, features="lxml"))
    deckURLs = html.split('"pretty_url":"')
    for x in range(len(deckURLs)):
        deckURLs[x] = deckURLs[x].split('"')[0]
    deckURLs.pop(0)
    return deckURLs

def createURL(limit=200000, filename="urlList.csv"):
    #Creates a csv file with URL for each topping decklist.
    urlList = []
    for x in range(round(limit/20)+1):
        try:
            urlList.extend(getPageURL(offset=(x*20), limit=limit))
            if x%20 == 0:
                print(str(x) + ": " + str(urlList[-1]))
        except:
            break
    df = pd.DataFrame({'url': urlList})
    if filename == "new":
        return df
    else:
        id = []
        for x in df["url"].to_list():
            id.append(int(np.char.rpartition(x, "-")[2]))
        df["id"] = id
        df = df.sort_values(by="id", ascending=True)
        df.to_csv(filename, sep='|', index=False)
        return

def updateURL(limit=200000, filename="urlList.csv"):
    #Updates existing deck URL file with newly added decks. Returns list of URLs of new decks.
    oldList = pd.read_csv("urlList.csv", sep="|")
    newList = createURL(limit=limit, filename="new")
    new = newList["url"].to_list()
    old = oldList["url"].to_list()
    diff = list(set(new)-set(old))
    if len(diff) > 0:
        print("--New decklist being added:")
        for currDeck in diff:
            oldList.loc[len(oldList.index)] = [currDeck, int(np.char.rpartition(currDeck, "-")[2])]
            print(currDeck)
    else:
        print("--No new decklist available.")
    oldList = oldList.sort_values(by="id", ascending=True)
    oldList.to_csv(filename, sep="|", index=False)
    newList.to_csv("newURLList.csv", sep="|", index=False)
    return diff

def getDeckList(url, id):
    #scrapes the decklist from the URL and returns a dataframe with all cards and deck metadata
    url = "https://ygoprodeck.com/deck/" + url
    req = requests.get(url, headers={'User-Agent': 'XYZ/3.0'}).text
    html = bs(req, features="lxml")
    
    date = html.find(class_="deck-metadata-info").find_all("span")[len(html.find(class_="deck-metadata-info").find_all("span"))-1].get_text()
    date = date[1:].replace("st","").replace("nd","").replace("rd","").replace("th","")
    formatedDate = datetime.strptime(date, '%b %d %Y')

    tagAndFormat = html.find(class_="deck-metadata-container deck-bgimg").find_all("a")
    format, formatFlag, tags = "", 0, []
    for x in range(len(tagAndFormat)):
        if formatFlag == 1:
            tags.append(tagAndFormat[x].get_text())
        if tagAndFormat[x].get_text() == "Tournament Meta Decks":
            format = "TCG"
            formatFlag = 1
        elif tagAndFormat[x].get_text() == "Tournament Meta Decks OCG":
            format = "OCG"
            formatFlag = 1
        elif tagAndFormat[x].get_text() == "Tournament Meta Decks OCG (Asian-English)":
            format = "OCG(Asia-English)"
            formatFlag = 1
        elif tagAndFormat[x].get_text() == "Tournament Meta Decks Worlds":
            format = "Worlds(TCG)"
            formatFlag = 1
        elif tagAndFormat[x].get_text() == " Master Duel Decks":
            format = "Worlds(MasterDuel)"
            formatFlag = 1

    
    nameList, typeList, deckList, codeList, imgSourceList, count = [], [], [], [], [], []
    for deckType in ["main_deck", "extra_deck", "side_deck"]:
        for type in html.find_all(id=deckType):
            for types in type.find_all(class_="lazy"):
                nameList.append(types.get("data-cardname"))
                typeList.append(types.get("data-cardtype"))
                codeList.append(types.get("data-name"))
                imgSourceList.append(types.get("data-src"))
                deckList.append(deckType)
    
    tagLen = len(tags)
    tag1, tag2, tag3 = "", "", ""
    if tagLen >= 1:
        tag1 = tags[0]
    if tagLen >= 2:
        tag2 = tags[1]
    if tagLen == 3:
        tag3 = tags[2]

    df = pd.DataFrame({"name": nameList, "type": typeList, "deck": deckList, "code": codeList, "imgSource": imgSourceList})
    df["deckID"], df["date"], df["format"], df["tag1"], df["tag2"], df["tag3"] = id, formatedDate, format, tag1, tag2, tag3
    return df

def createCardList(urlListFile, cardListFile=""):
    urlDF = pd.read_csv(urlListFile, delimiter="|")
    urlList = urlDF["url"].to_list()
    idList = urlDF["id"].to_list()
    decklistDF = getDeckList(urlList[0], idList[0])
    for x in range(1, len(urlList)):
        decklist = getDeckList(urlList[x], idList[x])
        decklistDF = pd.concat([decklistDF, decklist])
        if x%20 == 0:
            print(str(x) + ": " + str(urlList[x]))
    decklistDF = decklistDF.reset_index(drop=True)
    if cardListFile != "":
        decklistDF.to_csv(cardListFile, sep='|', index=False)
    return decklistDF

def updateCardList(newURLListFile, cardListFile):
    decklistDF = pd.read_csv(cardListFile, delimiter="|")
    newdeckListDF = createCardList(newURLListFile)
    decklistDF = pd.concat([decklistDF, newdeckListDF])
    decklistDF.to_csv(cardListFile, sep='|', index=False)
    return


#createCardList("urlTest.csv", "testtest.csv")

#x = pd.read_csv("testDeckList.csv", sep="|")
#print(x[x["tag1"]=="Snake-Eye"])

#getDeckList("tenpai-dragon-528657", 528657).to_csv("decklist.csv", sep="|")

#figure out the formating of the decklist to be examined later:
#Prob have a main tag and sub tag sections

#print(updateURL(40))

#createURL()
#updateURL(limit=20)

