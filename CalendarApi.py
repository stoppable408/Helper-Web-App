try:
    from modules import DateUtils
    from modules import contactUtils
    from modules import FormatUtils
except: 
    import DateUtils
    import contactUtils
    import FormatUtils

class CalendarAPI():

    def __init__(self):
        import requests
        import json
        self.requests = requests
        self.json = json
        self.calendarId = "8qdue9eg38bf5k8udtcqp66l7s@group.calendar.google.com"
        self.baseURI = "https://www.googleapis.com/calendar/v3/calendars"
        self.getToken()

    def getToken(self):
        import os
        import httplib2
        from oauth2client import file as oauthFile
        try:
            try:
                storage = oauthFile.Storage(os.getcwd() + r"\modules\calendar.dat")
            except:
                storage = oauthFile.Storage(os.getcwd() + r"\calendar.dat")
            credentials = storage.get()
            credentials.refresh(httplib2.Http())
            self.auth = {'Content-type': 'application/json', "Authorization": "OAuth %s" % credentials.access_token}
        except Exception as e:
            print(e)
            print("dfa file not found")

    def findEventByName(self, name):
        url = self.baseURI + "/" + self.calendarId +  "/events"
        r = self.requests.get(url, headers=self.auth)
        response = self.json.loads(r.text)["items"]
        event = [x for x in response if x["summary"] in name]
        return event[0]

    def listEvents(self, availability=False):
        def sortByDate(elem):
            return elem["start"]
        url = self.baseURI + "/" + self.calendarId +  "/events"
        r = self.requests.get(url, headers=self.auth)
        print(r.status_code)
        response = self.json.loads(r.text)["items"]
        for item in response:
            item["start"] = DateUtils.standardizeDate(item["start"])
            item["end"] = DateUtils.standardizeDate(item["end"])
        if availability == True:
            events = sorted([x for x in response if "Available" in x["summary"]], key=sortByDate)
            events = [(x["summary"],DateUtils.rewriteDate(x["start"]), x["id"]) for x in events if DateUtils.compareDate(x["start"])]
            return events
        else:
            events = sorted([x for x in response if "Available" not in x["summary"]], key=sortByDate)
            events = [str(DateUtils.datetimeToGameDate(x["start"],x["end"]) + " " + x["summary"]) for x in events if DateUtils.compareDate(x["start"])]
            return events

    def removeMember(self, personName, sessionDate, region):
        def parseDescription(description):
            nonlocal personName
            individualNum = description.split("\n")
            firstName = personName.split(" ")[0]
            for item in range(0,len(individualNum)):
                if firstName in individualNum[item]:
                    individualNum[item] = individualNum[item][0:2]
            return "\n".join(individualNum)
        def increaseSeats(summary):
            summary = summary.split()
            if summary[0] == "FULL":
                summary[0] = "1"
                summary[1] = "Seat"
            else:
                summary[0] = str(int(summary[0]) + 1)
            return " ".join(summary)
        contactobj = contactUtils.getContacts()
        events = self.listEvents()
        exactEvent = [x for x in events if sessionDate in x and region in x]
        calendarEvent = self.findEventByName(exactEvent[0])
        email = contactobj[personName][0]
        calendarEvent["attendees"] = [x for x in calendarEvent["attendees"] if x["email"] != email]
        calendarEvent["description"] = parseDescription(calendarEvent["description"])
        calendarEvent["summary"] = increaseSeats(calendarEvent["summary"])
        value = self.updateEvent(calendarEvent)
        return value

    def addMember(self, personName, description, sessionDate, region, waitlist=False):
        def modifysummaryString(firstName, description):
            return firstName + " - " + description
        def parseDescription(sessionDescription, characterDescription, waitlist):
            individualNum = sessionDescription.split("\n")
            if waitlist:
                individualNum.append(characterDescription)
            else:
                for num in range(0,len(individualNum)):
                    if len(individualNum[num]) > 2 or len(individualNum[num]) < 2:
                        continue
                    else:
                        individualNum[num] += " " + characterDescription
                        break
            return "\n".join(individualNum)
        def reduceSeats(summary):
            summary = summary.split()
            summary[0] = str(int(summary[0])- 1)
            if int(summary[0]) == 1:
                summary[1] = "Seat"
            if int(summary[0]) == 0:
                summary[0] = "FULL"
                summary[1] = ""
            summary = " ".join(summary)
            return summary
        firstName = personName.split(" ")[0]
        characterDescription = modifysummaryString(firstName,description)
        contactList = contactUtils.getContacts()
        events = self.listEvents()
        exactEvent = [x for x in events if sessionDate in x and region in x]
        calendarEvent = self.findEventByName(exactEvent[0])
        calendarEvent["description"] = parseDescription(calendarEvent["description"], characterDescription, waitlist)
        if not waitlist:
            email = contactList[personName][0]
            calendarEvent['attendees'].append({"email":email})
            calendarEvent["summary"] = reduceSeats(calendarEvent["summary"])
        value = self.updateEvent(calendarEvent, waitlist)
        return value

    def addEvent(self, body):
        url = self.baseURI + "/" + self.calendarId +  "/events"
        r = self.requests.post(url, headers=self.auth, data=self.json.dumps(body))
        if r.status_code == 200:
            return (True,"")
        else:
            return (False,r.text)         

    def updateEvent(self, event, waitlist=False):
        if waitlist:
            url = self.baseURI + "/" + self.calendarId +  "/events/" + event["id"] +"?sendUpdates=none"
        else:
            url = self.baseURI + "/" + self.calendarId +  "/events/" + event["id"] +"?sendUpdates=all"
        r = self.requests.patch(url, headers=self.auth, data=self.json.dumps(event))
        if r.status_code == 200:
            return True
        else:
            error = r.text
            print(error)
            return False

    def removeEvent(self, event):
        url = self.baseURI + "/" + self.calendarId +  "/events/" + event
        r = self.requests.delete(url, headers=self.auth)
        print(r.status_code)
        if r.status_code == 200 or r.status_code == 204:
            return (True,"")
        else:
            return (False,r.text)        


    def listEvent(self):
        url = self.baseURI + "/" + self.calendarId +  "/events/"
        r = self.requests.get(url, headers=self.auth)
        if r.status_code == 200:
            response = self.json.loads(r.text)
            for event in response["items"]:
                event["start"] = DateUtils.standardizeDate(event["start"])
                event["end"] = DateUtils.standardizeDate(event["end"])
            return response["items"]

        
        
