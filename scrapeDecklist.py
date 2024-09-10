import pandas as pd
from urllib.request import Request, urlopen
import urllib.parse
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime


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

def getDeckURL(archetype, offset=0, limit=100):
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

def getURLs(archetype, limit=100):
    #Gets all deck urls from search results. Does round up limit to the nearest 20s to make it easier.
    urlList = []
    for x in range(round(limit/20)+1):
        try:
            urlList.append(getDeckURL(archetype, offset=(x*20), limit=limit))
        except:
            break
    allurls = [j for i in urlList for j in i]
    return allurls

  
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
    df.to_csv("archetypes.csv",sep="|", index=False)
    return df

def updateArchetypeFile():
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
    else:
        print("--No new archetypes added.")
    return



#createArchetypeFile()
#print("done")
updateArchetypeFile()






#Run this shit, find archetypes with zero hits and figure out why that is the case.
