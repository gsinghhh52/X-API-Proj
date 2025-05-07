#Language: Python

#Description: This program returns the marker url for the marker for the currently displayed tweet for the 'Maps-Twitter-Project.'

def generateMarkerString(currentTweetIndex, tweetLatLonList, mapCenterLatLon):
    stringRed = '&markers=color:red|'
    stringBlue = '&markers=color:blue|size:small|'
    twitterMarkerURL = ''
    currentTweetIndex = currentTweetIndex
    tweetLatLonList = tweetLatLonList
    mapCenterLatLon = mapCenterLatLon
    for index in range(len(tweetLatLonList)):
        if (tweetLatLonList[index] == None):
            tweetLatLonList[index] = mapCenterLatLon

    stringRed = stringRed + str(tweetLatLonList[currentTweetIndex][0]) + ','
    stringRed = stringRed + str(tweetLatLonList[currentTweetIndex][1])
    #print(stringRed)

    index = 0
    while index < len(tweetLatLonList):
        if(index != currentTweetIndex) and tweetLatLonList[index] != tweetLatLonList[currentTweetIndex]:
            stringBlue = stringBlue + (str(tweetLatLonList[index][0])) + ','
            stringBlue = stringBlue + (str(tweetLatLonList[index][1]))
            stringBlue = stringBlue + ('|')
        index += 1


    #print(stringBlue[:-1])
    twitterMarkerURL = stringRed + stringBlue[:-1]
    #print(twitterMarkerURL)
    return twitterMarkerURL

#print(generateMarkerString(1, [[40.7452888, -73.9864273], None, [40.76056, -73.9659]], [40.758895, -73.985131]))
