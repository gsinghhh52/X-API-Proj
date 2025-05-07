import tkinter
from tkinter import Tk, Canvas, Frame, Button, Label, Entry, END, LEFT, BOTTOM, TOP, RIGHT, SUNKEN
import math
import ssl
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlencode, quote_plus
import json
import oauth2 as oauth
from urllib.parse import quote_plus
from twitteraccess import *
from generateMarkerString import *
import webbrowser

global lat, lng, urlIndex
lat = 0
lng = 0
urlIndex = 0


GOOGLEAPIKEY = "AIzaSyCSKoYf7PqR5gfAe8I_hLGTmVciV616Ij0"

class Globals:
    rootWindow = None
    mapLabel = None
    locationEntry = None
    searchEntry = None
    defaultLocation = "Mauna Kea, Hawaii"
    mapLocation = defaultLocation
    mapFileName = 'googlemap.gif'
    mapSize = 400
    zoomLevel = 9
    mapType = 'roadmap'
    tweets = None
    currentTweetIndex = 0
    currentTweetUrlIndex = 0
    TweetNum = 0
    markerUrl = None


# Given a string representing a location, return 2-element tuple
# (latitude, longitude) for that location
#
# See https://developers.google.com/maps/documentation/geocoding/
# for details
#

def geocodeAddress(addressString):
    urlbase = "https://maps.googleapis.com/maps/api/geocode/json?address="
    geoURL = urlbase + quote_plus(addressString)
    geoURL = geoURL + "&key=" + GOOGLEAPIKEY

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    stringResultFromGoogle = urlopen(geoURL, context=ctx).read().decode('utf8')
    jsonResult = json.loads(stringResultFromGoogle)
    if (jsonResult['status'] != "OK"):
        print("Status returned from Google geocoder *not* OK: {}".format(jsonResult['status']))
        return (0.0, 0.0)  # this prevents crash in retrieveMapFromGoogle - yields maps with lat/lon center at 0.0, 0.0
    loc = jsonResult['results'][0]['geometry']['location']
    return (float(loc['lat']), float(loc['lng']))

def getMapUrl(lat, lng):
    urlbase = "http://maps.google.com/maps/api/staticmap?"
    args = "center={},{}&zoom={}&size={}x{}&maptype={}&{},{}{}&sensor=false&format=gif".format(lat, lng, Globals.zoomLevel, Globals.mapSize,
                                                               Globals.mapSize,Globals.mapType,lat,lng,Globals.markerUrl)
    args = args + "&key=" + GOOGLEAPIKEY
    mapURL = urlbase + args
    return mapURL

def retrieveMapFromGoogle():
    global lat, lng, mapCenterLatLon
    lat, lng = geocodeAddress(Globals.mapLocation)
    mapCenterLatLon = (lat,lng)
    url = getMapUrl(lat, lng)
    urlretrieve(url, Globals.mapFileName)


##########
#  basic GUI code

def displayMap():
    retrieveMapFromGoogle()
    mapImage = tkinter.PhotoImage(file=Globals.mapFileName)
    Globals.mapLabel.configure(image=mapImage)
    # next line necessary to "prevent (image) from being garbage collected" - http://effbot.org/tkinterbook/label.htm
    Globals.mapLabel.mapImage = mapImage

def readEntriesSearchTwitterAndDisplayMap():
    global lat, lng, tweetPrintLabel, tweetLatLonList, screenNamesList, nameList, urlList, urlIndex, urlPrintLabel
    global mapCenterLatLon
    #print('function entered')
    Globals.currentTweetIndex = 0
    Globals.TweetNum = 1
    urlIndex = 0
    locationString = Globals.locationEntry.get()
    Globals.mapLocation = locationString
    lat, lng = geocodeAddress(Globals.mapLocation)
    getTweetsFromLocation()
    tweetPrintLabel.configure(text=printable(tweetsList[Globals.currentTweetIndex]))
    currentTweetNumLabel.configure(text='Tweet # {} of {}'.format('1', len(tweetsList)))
    screenNamePrintLabel.configure(text='@'+printable(screenNamesList[Globals.currentTweetIndex]))
    namePrintLabel.configure(text=printable(nameList[Globals.currentTweetIndex]))
    urlList = []
    tweetIndex = 0
    for ele in (Globals.tweets):
        urlList.append([])
        for url in ele['entities']['urls']:
            urlList[tweetIndex].append(url['expanded_url'])
        tweetIndex += 1
    urlPrintLabel.configure(text = urlList[Globals.currentTweetIndex][urlIndex])
    Globals.markerUrl = generateMarkerString(Globals.currentTweetIndex, tweetLatLonList, mapCenterLatLon)
    displayMap()
    #print(urlList)

def nextUrl():
    global urlList, urlPrintLabel,urlIndex
    if urlIndex < len(urlList[Globals.currentTweetIndex])-1:
        urlIndex += 1
        urlPrintLabel.configure(text=urlList[Globals.currentTweetIndex][urlIndex])

def prevUrl():
    global urlList, urlPrintLabel, urlIndex
    if urlIndex >= 1:
        urlIndex -= 1
        urlPrintLabel.configure(text=urlList[Globals.currentTweetIndex][urlIndex])

def nextTweet():
    global tweetsList,currentTweetNumLabel,tweetLatLonList, screenNamesList, nameList,screenNamePrintLabe,namePrintLabel
    global mapCenterLatLon
    if (Globals.currentTweetIndex + 1 != len(tweetsList)):
        Globals.currentTweetIndex += 1
        Globals.TweetNum += 1
        Globals.markerUrl = generateMarkerString(Globals.currentTweetIndex, tweetLatLonList, mapCenterLatLon)
        tweetPrintLabel.configure(text=printable(tweetsList[Globals.currentTweetIndex]))
        screenNamePrintLabel.configure(text='@'+printable(screenNamesList[Globals.currentTweetIndex]))
        namePrintLabel.configure(text=printable(nameList[Globals.currentTweetIndex]))
        currentTweetNumLabel.configure(text='Tweet # {} of {}'.format(Globals.TweetNum,len(tweetsList)))
        displayMap()


def prevTweet():
    global tweetsList,currentTweetNumLabel,namePrintLabel, screenNamePrintLable
    if (Globals.currentTweetIndex - 1 != len(tweetsList)-1 and Globals.currentTweetIndex - 1 >= 0):
        Globals.currentTweetIndex -= 1
        Globals.TweetNum -= 1
        Globals.markerUrl = generateMarkerString(Globals.currentTweetIndex, tweetLatLonList, mapCenterLatLon)
        tweetPrintLabel.configure(text=printable(tweetsList[Globals.currentTweetIndex]))
        tweetPrintLabel.configure(text=printable(tweetsList[Globals.currentTweetIndex]))
        screenNamePrintLabel.configure(text='@'+printable(screenNamesList[Globals.currentTweetIndex]))
        namePrintLabel.configure(text=printable(nameList[Globals.currentTweetIndex]))
        currentTweetNumLabel.configure(text='Tweet # {} out of {}'.format(Globals.TweetNum,len(tweetsList)))
        displayMap()

#function for being able to zoom in
def ZoomIn():
   Globals.zoomLevel += 1
   displayMap()

#function for being able to zoom out
def ZoomOut():
    Globals.zoomLevel -= 1
    displayMap()

def radioButtonChosen():
    global selectedButtonText
    global choiceVar
    global label

    if choiceVar.get() == 1:
        selectedButtonText = "roadmap"
        Globals.mapType = "roadmap"
    elif choiceVar.get() == 2:
        selectedButtonText = "satellite"
        Globals.mapType = "satellite"
    elif choiceVar.get() == 3:
        selectedButtonText = "terrain"
        Globals.mapType = "terrain"
    else:
        selectedButtonText = "hybrid"
        Globals.mapType = "hybrid"
    displayMap()
    label.configure(text="Radio button choice is: {}".format(selectedButtonText))

def openUrl():
    global urlList,urlIndex
    if urlIndex < len(urlList[Globals.currentTweetIndex]):
        if(urlList[Globals.currentTweetIndex][urlIndex] != None):
            webbrowser.open(urlList[Globals.currentTweetIndex][urlIndex])

def initializeGUIetc():
    global selectedButtonText, choiceVar, label, tweetsList, tweetPrintLabel,currentTweetNumLabel,urlPrintLabel,namePrintLabel
    global screenNamePrintLabel, urlList, urlIndex

    Globals.rootWindow = tkinter.Tk()
    Globals.rootWindow.title("HW9")

    locationLabelFrame = tkinter.Frame(Globals.rootWindow)
    locationLabel = Label(locationLabelFrame, text="Enter the location:")
    locationLabelFrame.pack()
    locationLabel.pack()

    Globals.locationEntry = tkinter.Entry()
    Globals.locationEntry.pack()

    seachTermFrame = tkinter.Frame(Globals.rootWindow)
    seachTermFrame.pack()
    seachTermLabel = Label(seachTermFrame, text="Enter your search term:")
    seachTermLabel.pack()

    Globals.searchEntry = tkinter.Entry()
    Globals.searchEntry.pack()

    mainFrame = tkinter.Frame(Globals.rootWindow)
    mainFrame.pack()

   
    readEntriesSearchTwitterAndDisplayMapButton = tkinter.Button(mainFrame, text="Show me the map!", command=readEntriesSearchTwitterAndDisplayMap)
    readEntriesSearchTwitterAndDisplayMapButton.pack()

    ZoomInButton = tkinter.Button(mainFrame,text="+", command=ZoomIn)
    ZoomInButton.pack()

    ZoomOutButton = tkinter.Button(mainFrame,text="-",command=ZoomOut)
    ZoomOutButton.pack()

    selectedButtonText = ""
    choiceVar = tkinter.IntVar()
    choiceVar.set(1)
    choice1 = tkinter.Radiobutton(mainFrame, text="Road Map View", variable=choiceVar, value=1,command=radioButtonChosen)
    choice1.pack()
    choice2 = tkinter.Radiobutton(mainFrame, text="Satellite Map View", variable=choiceVar, value=2, command=radioButtonChosen)
    choice2.pack()
    choice3 = tkinter.Radiobutton(mainFrame,text="Terrain Map View", variable=choiceVar,value=3,command=radioButtonChosen)
    choice3.pack()
    choice4 = tkinter.Radiobutton(mainFrame,text="Hybrid Map View", variable=choiceVar,value=4,command=radioButtonChosen)
    choice4.pack()

    label = tkinter.Label(mainFrame, text="radio button choice is: {}".format(selectedButtonText))
    label.pack()

    twitterTitleLabel = tkinter.Label(mainFrame, text='Twitter Information:')
    twitterTitleLabel.pack()

    tweetPrintLabel = tkinter.Label(mainFrame)
    tweetPrintLabel.pack()

    screenNamePrintLabel = tkinter.Label(mainFrame)
    screenNamePrintLabel.pack()

    namePrintLabel = tkinter.Label(mainFrame)
    namePrintLabel.pack()

    nextTweetButton = tkinter.Button(mainFrame, text='Next Tweet', command=nextTweet)
    nextTweetButton.pack()

    prevTweetButton = tkinter.Button(mainFrame, text='Previous Tweet', command=prevTweet)
    prevTweetButton.pack()

    currentTweetNumLabel = tkinter.Label(mainFrame)
    currentTweetNumLabel.pack()
    Globals.TweetNum += 1

    urlPrintLabel = tkinter.Label(mainFrame)
    urlPrintLabel.pack()

    nextUrlButton = tkinter.Button(mainFrame,text='Next Url',command=nextUrl)
    nextUrlButton.pack()

    prevUrlButton = tkinter.Button(mainFrame,text='Previous Url',command=prevUrl)
    prevUrlButton.pack()

    urlButton = tkinter.Button(mainFrame,text='Open Url',command=openUrl)
    urlButton.pack()
    # we use a tkinter Label to display the map image
    Globals.mapLabel = tkinter.Label(mainFrame, width=Globals.mapSize, bd=2, relief=tkinter.FLAT)
    Globals.mapLabel.pack()


def getTweetsFromLocation():
    global lat, lng,tweetsList,tweetLatLonList, screenNamesList, nameList, urlList
    tweetLatLonList = []
    tweetsList = []
    screenNamesList= []
    nameList = []
    urlList = []
    latLng= [lat,lng]
    searchTerm = Globals.searchEntry.get()
    print("Searching for", searchTerm, "around", latLng[0], ",", latLng[1])
    Globals.tweets = searchTwitter(searchTerm, latlngcenter=latLng)

    #iterate through the twitter dictionary (global.tweets in this case)
        #put all of the lat and longitude into a list called tweetLatLonList
        #put all of the tweets in a list as well
        #put all of the screen names into a list
        #put all of the names into a list

    
    for ele in Globals.tweets:
        if(ele['coordinates'] == None):
            tweetLatLonList.append(latLng)
        else:
            tweetLatLonList.append(ele['coordinates']['coordinates'])
        tweetsList.append(ele['text'])
        screenNamesList.append(ele['user']['screen_name'])
        nameList.append(printable(ele['user']['name']))

    for ele in tweetLatLonList:
        var1 = ele[0]
        var2 = ele[1]
        ele[0],ele[1] = var2, var1

    
def HW9():
    authTwitter()
    initializeGUIetc()
    displayMap()
    Globals.rootWindow.mainloop()
    getTweetsFromLocation()

HW9()
