import os,sys
import random
from flask import Flask, request
from pymessenger.bot import Bot
from fbmq import Page
import datetime
import sqlite3
from sqlite3 import Error
from difflib import SequenceMatcher
import difflib
countt=0
docID=0
patID=0
all_ids_have_initial_message=[]
allSymptoms=[]
initialSymptoms=[]

app = Flask(__name__)
ACCESS_TOKEN = 'EAAPIwZBLbqA4BALTmeDZAZCvbgQORt3Bsbib50ewOq3TWlVcZAso7e1WKgPz2ayuWA2OPkZBS5Bi4Cp9TDM3b6IF5h1ZCMnHXqZA4gG0BlpCGU0Rs93GM715sCiKCbHcVZBf9OZAerGBSqZBLFKPVM2qNV7MslEdMLU3O3i60GxWNRzToZCbn00ruF3'
VERIFY_TOKEN = 'hello#100'
bot=Bot(ACCESS_TOKEN)
page = Page(ACCESS_TOKEN)



@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
    # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                timeee=str(datetime.datetime.today().strftime('%Y-%m-%d'))
                if message['message'].get('text'):
                    firstText=message['message'].get('text')# get_message()
                    user_name=""
                    doctorsList=[]
                    patientList=[]
                    if not message['message'].get('is_echo'):
                        user_profile = page.get_user_profile(recipient_id)
                        user_name=user_profile['first_name']
                        
                        response_sent_text=""
                        conn=sqlite3.connect('all-data-shaksny.db')
                        cur1=conn.execute("SELECT id from user")
                        patientList=cur1.fetchall()
                        conn.commit()
                        cur2=conn.execute("SELECT id from doctor")
                        doctorsList=cur2.fetchall()
                        
                        conn.commit()
                        docList=[]
                        for item in doctorsList:
                            docList.append(item[0])
                        patList=[]
                        for item in patientList:
                            patList.append(item[0])
                            
                        if countt==0:
                            if (recipient_id not in patList) and (recipient_id not in docList):
                                global all_ids_have_initial_message
                                if (recipient_id not in all_ids_have_initial_message) :
                                    all_ids_have_initial_message.append(recipient_id)
                                    send_message(recipient_id,"Hey <3 .. Please tell me, are you patient or doctor ? ")
                                if "patient" in firstText or "Patient" in firstText or "PATIENT" in firstText:
                                    cur3=conn.execute("INSERT INTO user (id, date, mess, conversation) VALUES (?,?,?,?)" ,(recipient_id, timeee, firstText, "unfinished" ))
                                    conn.commit()
                                    send_message(recipient_id,"welcome "+user_name+" <3 ")
                                    send_message(recipient_id, "Please describe what do you feel in detail to help you ^_^ ")
                                elif "doctor" in firstText or "Doctor" in firstText or  "DOCTOR" in firstText or  "DR" in firstText or "Dr" in firstText or "dr" in firstText :
                                    cur4=conn.execute("INSERT INTO doctor (id, specialty ) VALUES (?,?)" ,(recipient_id, "None" ))
                                    conn.commit()
                                    send_message(recipient_id,"welcome Dr "+user_name+" <3 ")
                                    send_message(recipient_id, "Shakhsny Bot family happy for joining you with us to help patients <3  we will send messages to you when patient need to communicate with you  ^_^ ")
                                    
                            else:
                                if recipient_id in patList:
                                    flag = False
                                    countP=0
                                    for item in patList:
                                        if recipient_id == item:
                                            countP+=1
                                    if countP >0:
                                        cur5=conn.execute("SELECT conversation from user where id="+recipient_id)
                                        conn.commit()
                                        for item in cur5:
                                            if item[0] == "unfinished":
                                                flag= True
                                        if flag == True:
                                            cur7=conn.execute("SELECT mess from user where id="+recipient_id+" and conversation='unfinished'")
                                            messages=""
                                            for rows in cur7:
                                                messages+=rows[0]
                                            messages+=","+firstText
                                            conn.execute("UPDATE user set mess= ? where id= ? and conversation= ?", (messages,recipient_id,'unfinished'))
                                            conn.commit()
                                        else:
                                            cur6=conn.execute("INSERT INTO user (id, date, mess, conversation) VALUES (?,?,?,?)" ,(recipient_id, timeee, firstText, "unfinished" ))
                                            conn.commit()
                                        
                        cur8 =conn.execute("SELECT mess from user where id="+recipient_id+" and conversation='unfinished'")
                        for item in cur8:
                            response_sent_text+=item[0]
                        conn.commit()
                        conn.close()
                        all_conversation(response_sent_text,firstText,patList,docList,recipient_id,user_name)

                            
                if message['message'].get('attachments'):
                    firstText ="No text" #get_message()
                    send_message(recipient_id, firstText)
                        
                   
                    
                
    return "Message Processed"

def similar(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()
    
def all_conversation(response_sent_text,firstText,patientList,doctorsList,recipient_id,user_name):
    words=["No", "no", "NO", "Yes", "YES" ,"yes" ,"patient","Patient","PATIENT","DOCTOR","doctor","Doctor","dr","Dr","DR","Welcome","welcome","Hello","hello","Hi","hi","Hey","hey","Good Afternoon","good afternoon","good morning","Good Morning","Good Evening","good evening"]
    global countt
    if countt == 0:
        if recipient_id not in patientList:
            if  "thanks" in firstText or "thank you" in firstText :
                send_message(recipient_id, "you are welcome Dr "+user_name+" <3 ")
            elif "ok" in firstText or "Ok" in firstText or "OK" in firstText or "Okay" in firstText or "okay" in firstText or "OKAY" in firstText:
                send_message(recipient_id, "ok Dr "+user_name+" <3 "+" thank you ^_^ ")
            elif "good bye" in firstText or "Good Bye" in firstText or "Good bye" in firstText or "bye" in firstText or "Bye" in firstText:
                send_message(recipient_id,firstText+" Dr "+user_name+" ^_^ ")
            elif similar(firstText,"i have swollen in breasts i have lumps in my breasts i have tumors in my breasts i have tumefy in my breasts i have tumor in my breasts i have neoplasm in my breasts i have growth in my breasts i have tumefaction in my breasts the breast may be painful when touched but does not suffer pain if do not touch it") <0.01 and firstText not in words and ("patient" not in firstText or "Patient" not in firstText or "PATIENT" not in firstText or "doctor" not in firstText or "Doctor" not in firstText or "DOCTOR" not in firstText or "DR" not in firstText or "dr" not in firstText or "Dr" not in firstText ):
                send_message(recipient_id, "Sorry I can not understand your words :( ")
        else:
            if  "thanks" in firstText or "thank you" in firstText :
                send_message(recipient_id, "you are welcome "+user_name+" <3 i hope that i will help you ^_^ ")
                
            elif "ok" in firstText or "Ok" in firstText or "OK" in firstText or "Okay" in firstText or "okay" in firstText or "OKAY" in firstText:
                send_message(recipient_id, "ok "+user_name+" <3 ")
                
            elif "good bye" in firstText or "Good Bye" in firstText or "Good bye" in firstText or "bye" in firstText or "Bye" in firstText:
                send_message(recipient_id,firstText+" "+user_name+" <3 i wish you getting better soon ^_^ ")
                
            elif similar(firstText,"i have swollen in breasts i have lumps in my breasts i have tumors in my breasts i have tumefy in my breasts i have tumor in my breasts i have neoplasm in my breasts i have growth in my breasts i have tumefaction in my breasts the breast may be painful when touched but does not suffer pain if do not touch it") <0.01 and firstText not in words and ("patient" not in firstText or "Patient" not in firstText or "PATIENT" not in firstText or "doctor" not in firstText or "Doctor" not in firstText or "DOCTOR" not in firstText or "DR" not in firstText or "dr" not in firstText or "Dr" not in firstText ):
                send_message(recipient_id, "Sorry I can not understand your words :( Please describe what you feel ^_^ ")
                
            elif similar(firstText,"What is the information about?") >=0.6 or similar(firstText,"I want/need to know information about") >=0.6 or similar(firstText,"Please I want/need to know information about") >=0.6 or similar(firstText,"I do not know any information at and I want to know information about it please") >=0.6 or similar(firstText,"Could you tell me any information about?") >=0.6:
                co=sqlite3.connect('all-data-shaksny.db')        
                cu=co.execute("SELECT name FROM diseases")
                co.commit()
                count=0
                allDiseaseNames = cu.fetchall()
                for item in allDiseaseNames:
                    if item[0] in firstText or item[0] in firstText.title() or item[0] in firstText.upper() or item[0] in firstText.capitalize():
                        count=count+1
                        targetDisease=item[0]
                if count > 0:
                    r=co.execute("SELECT info FROM diseases WHERE name= ?", (targetDisease,))
                    message=r.fetchall()
                    co.commit()
                    co.close()
                    send_message(recipient_id, message[0][0])
                else:
                    send_message(recipient_id,"Sorry we don't have any information about this disease right now :( ")
            else:
                connect=sqlite3.connect('all-data-shaksny.db')        
                cursor3=connect.execute("SELECT description FROM symptoms")
                connect.commit()
                description = cursor3.fetchall()
                
                outerlist=[]
                for item in description:
                    ratio =similar(response_sent_text,item[0])
                    outerlist.append([ratio,item[0]])
                    
                outerlist.sort(key=lambda x: x[0])
                    
                    
                knearestList=[]
                targetSym=[]
                desc_list = [item[1] for item in outerlist]
                ratio = [item[0] for item in outerlist]
                for i in range(len(ratio)):
                    if ratio[i] > 0.30:
                       targetSym.append(desc_list[i])
                for item in targetSym :
                    cursor4= connect.execute("SELECT name FROM symptoms WHERE description= ?", (item,))
                    sym=cursor4.fetchall()
                    knearestList.append(sym[0])
                connect.commit()    
                connect.close()
                finalSymptomsList=[]
                message=""
                aprioriList=getNameofsymptoms(2)
                for item in knearestList:
                    if item not in finalSymptomsList:
                        finalSymptomsList.append(item)
                    if item in aprioriList:
                        for itemm in aprioriList:
                            if itemm not in finalSymptomsList:
                                finalSymptomsList.append(itemm)
                
                global allSymptoms
                global initialSymptoms
                if len(finalSymptomsList)>0:
                    size1=len(allSymptoms)
                    for i in range(len(finalSymptomsList)):
                        if finalSymptomsList[i][0] not in allSymptoms :
                            allSymptoms.append(finalSymptomsList[i][0])
                    size2=len(allSymptoms)
                    message="Do you feel "
                    for i in range(len(finalSymptomsList)):
                        if finalSymptomsList[i][0] not in initialSymptoms:
                            initialSymptoms.append(finalSymptomsList[i][0])
                            message+=str(finalSymptomsList[i][0])
                            if i != len(finalSymptomsList):
                                message=message+" , "
                    if size1==size2:
                        send_message(recipient_id, "ok please wait a few minutes <3 I will tell you the disease now ^_^ ")
                        SymptomsIDs=[]
                        Diseases_IDs=[]
                        ct=sqlite3.connect('all-data-shaksny.db')
                        for item in allSymptoms:
                            cur1=ct.execute("SELECT symptoms_id FROM symptoms WHERE name= ?", (item,))
                            SymptomsIDs.append(cur1.fetchall())
                        ct.commit()
                        for item in SymptomsIDs:
                            cur2=ct.execute("SELECT diseases_id FROM diseases_symptoms_relation WHERE symptoms_id= ?", (item[0]))
                            Diseases_IDs.append(cur2.fetchall())
                        ct.commit()
                        SuccDiseases=[]
                        coun=[]
                        for item in Diseases_IDs:
                            tempCount=0
                            targetDisease=item
                            for item in Diseases_IDs:
                                if targetDisease==item:
                                    tempCount=tempCount+1
                            if targetDisease not in SuccDiseases:
                                SuccDiseases.append(targetDisease)
                                coun.append(tempCount)
                        maxCount=max(coun)
                        for i in range(len(coun)):
                            if coun[i]== maxCount:
                                cur3=ct.execute("SELECT name FROM diseases WHERE diseases_id= ?", (SuccDiseases[i][0]))
                                cur4=ct.execute("SELECT specialty FROM diseases WHERE diseases_id= ?", (SuccDiseases[i][0]))
                                txt="We recommend that you may be have "+str(cur3.fetchall()[0][0])+" and you need to visit a doctor in "+str(cur4.fetchall()[0][0])+" specialty"
                                send_message(recipient_id, txt)
                        ct.commit()
                        ct.close()
                        #Count=0
                        send_message(recipient_id,user_name+" <3 , Do you want to talk to a doctor ? ")
                        global patID
                        patID=recipient_id
                        countt+=1
                       
                            
                    else :
                        message=message+"?"
                        send_message(recipient_id, message)
                else:
                    message="ok "+user_name+" <3 please describe more details about what you feel ^_^ "
                    send_message(recipient_id, message)
                    
    elif countt>0:
        if countt == 1:
            if "yes" in firstText or "ok" in firstText or "agree" in firstText or "agreement" in firstText or "i wish" in firstText or "i want" in firstText:
                for item in doctorsList:
                    send_message(item,"Please Doctor, there is a patient who wants to communicate with you")
            else:
                send_message(recipient_id,"ok as you wish "+user_name+" <3 ")
                scon=sqlite3.connect('all-data-shaksny.db')
                scon.execute("UPDATE user set conversation= ? where id= ?", ('finished',recipient_id))
                scon.commit()
                scon.close()
            countt+=1
        else:
            if recipient_id not in patientList:
                global docID
                docID=recipient_id
            
            if recipient_id == patID:
                send_message(docID, firstText)
            else:
                send_message(patID, firstText)
            
            if recipient_id == patID and "bye" in firstText:
                scon=sqlite3.connect('all-data-shaksny.db')
                scon.execute("UPDATE user set conversation= ? where id= ?", ('finished',recipient_id))
                scon.commit()
                scon.close()
            
        
    return"ok"


def readfile():  # read from data base      #ok
    db = sqlite3.connect('all-data-shaksny.db')
    cr = db.cursor()

    cr.execute('select * from diseases_symptoms_relation ')
    lists = list()
    for row in cr.fetchall():
        lists.append(row)
    db.commit()
    return lists

def transaction():  # re_shape data base into transaction which each transaction with different id      #ok
    lists = readfile()
    Size = len(lists)
    i = 1
    count = 18  # type: int
    Transactions = []
    while i <= count:
        mytransaction = []
        j = 0
        while j < Size:
            if int(lists[j][0]) == i:
                mytransaction.insert(j, int(lists[j][1]))
            j = j + 1
        Transactions.insert(i, mytransaction)
        i = i + 1
    return Transactions


def symptom():  # store all symptom in list     #ok
    list1 = readfile()
    size = len(list1)
    x = 0
    symptoms = []
    while x < size:
        st = int(list1[x][1])
        symptoms.insert(x, st)
        x = x + 1
    return symptoms


def unique():  # get all unique symptoms       #ok
    symptoms = symptom()
    size = len(symptoms)
    uniqs = []
    x = 0
    while x < size:
        if symptoms[x] not in uniqs:
            uniqs.append(symptoms[x])
        x = x + 1
    return uniqs

def count_of_unique():  # ok
    uniques = unique()
    symptoms = symptom()
    counts_of_unique = []
    for i in range(0, len(uniques)):
        counter = 0
        counter = symptoms.count(uniques[i])
        counts_of_unique.insert(i, counter)
    return counts_of_unique


def remove_duplicate(list1):
    for i in range(0, len(list1)):
        list1[i].sort()

    new_k = []
    for elem in list1:
        if elem not in new_k:
            new_k.append(elem)
    k = new_k
    return k


def Apriori_prune(Ck, MinSupport):  # remove element that less than minimum support  #ok
    output = []
    trans = transaction()

    for i in range(0, len(Ck)):
        counter = 0
        if type(Ck[i]) == list:
            for j in range(len(trans)):
                if (set(Ck[i]).issubset(set(trans[j]))):
                    counter = counter + 1
            if counter >= MinSupport:
                output.append(Ck[i])
        else:
            for j in range(len(trans)):
                if Ck[i] in trans[j]:
                    counter = counter + 1
            if counter >= MinSupport:
                output.append(Ck[i])
    return output


def generator(mylist, lenght, minsupport):
    uni = unique()
    uniqs = Apriori_prune(uni, minsupport)
    # uniqs = [1, 2, 3, 4]
    finall = mylist
    for i in range(0, len(mylist)):
        if type(mylist[0]) != list:
            # generate 2 combination
            canditate = []
            for i in range(0, lenght):
                element = mylist[i]
                for j in range(i + 1, lenght):
                    element1 = mylist[j]
                    list1 = []
                    list1.append(element)
                    list1.append(element1)
                    canditate.append(list1)
            out = Apriori_prune(canditate, minsupport)
            if len(out) == 0:
                return finall

            # print "******************8***************************************************************************8"
            # print out
            out = remove_duplicate(out)
            # print out
            mylist = out
            finall = out
            ############################################################################################################
        else:
            # uniqs = [1, 2, 3, 4]
            while (True):
                outt = []
                for i in range(0, len(finall)):
                    for j in range(0, len(uniqs)):
                        index = finall[i]
                        if uniqs[j] not in index:
                            smli = []
                            for k in range(0, len(finall[i])):
                                smli.append(finall[i][k])
                            smli.append(uniqs[j])
                            outt.append(smli)
                #               print outt
                outt = list(remove_duplicate(outt))
                #  print len(outt)
                # print"====================================================="
                achieve_min_support = list(Apriori_prune(outt, minsupport))
                # print len(achieve_min_support)
                if len(achieve_min_support) == 0:
                    #    print "lol"
                    #   print finall
                    #  print len(finall)
                    return finall
                elif finall != achieve_min_support:
                  #  print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
                    finall = list(achieve_min_support)
                    # listof2 = list(achieve_min_support)
                    length = len(achieve_min_support)
                #print len(finall)
            return finall


def getNameofsymptoms(minsupport):
    uni = unique()
    # print uni
    # print len(uni)
    ls = Apriori_prune(uni, minsupport)
    # print ls
    two = generator(ls, len(ls), minsupport)
    #print two

    db1 = sqlite3.connect('all-data-shaksny.db')
    cr1 = db1.cursor()
    lists = list()
    for i in range(0, len(two)):
        list1 = []
        for j in range(0, len(two[i])):
            if type(two[i]) == list:
                cr1.execute('select name from symptoms where symptoms_id == ' + str(two[i][j]))
                for row in cr1.fetchall():
                    list1.append(row)
        lists.append(list1)
        db1.commit()
    return list1
                
def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    else:
        return 'Invalid verification token'

 
#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

    

if __name__ == "__main__":
    app.run(debug=True,port=3000)




