import mysql.connector
import random
import time

boxes_id = ["small", "medium", "large"]
gem_complects = ['<:tfive:913615358525583432>','<:tsix:913615358777233450>','<:modik24:913615095714693222>']

def getData():
    with open("data.txt", "r") as f:
        lines = f.read().rstrip()
        return lines

def getConnectedDB():
    from dhbot import bot
    if bot.db == None:
        bot.db = getConnection()
    elif bot.db.is_connected() == False:
        bot.db = getConnection()       
    return bot.db

def getConnection():
    print("CONNECTING")
    sqlData = getData()
    return mysql.connector.connect(
        host=sqlData[1],
        user=sqlData[2],
        password=sqlData[3],
        database=sqlData[4]
    )

def sendRequest(req):
    mydb = getConnectedDB()
    mycursor = mydb.cursor()
    mycursor.execute(req)
    mydb.commit()
    mycursor.close()

def sendGetRequest(req):
    mydb = getConnectedDB()
    mycursor = mydb.cursor()
    mycursor.execute(req)
    myresult = mycursor.fetchall()
    mycursor.close()
    return myresult

def getTop():
    return sendGetRequest("SELECT id, name, item, modif, amount FROM top ORDER BY modif DESC, amount DESC")

def saveCurrent(arg,name,mod):
    sendRequest("UPDATE current SET item='"+arg+"',modif="+str(mod)+",owner='"+name+"' WHERE id = 0")

def getCurrent():
    return sendGetRequest("SELECT item, owner, modif, owid FROM current WHERE id = 0")

def addBox(oid, boxn):
    myresult = sendGetRequest("SELECT small, medium, large FROM item WHERE id = "+str(oid)+"")
    if len(myresult)>0:
        addBoxToBase(oid,boxes_id[boxn])       
    else:
        setBoxWith(oid,boxes_id[boxn],1)
    return boxn

def setBoxesToZero(id):
    sendRequest("UPDATE item SET small = 0, medium = 0, large = 0 WHERE id = '"+str(id)+"'")

def addItems(tfive,tsix,modik,id):
    sendRequest("UPDATE item SET tfive = tfive + "+str(tfive)+", tsix = tsix + "+str(tsix)+", modik = modik + "+str(modik)+" WHERE id = '"+str(id)+"'")

def getItemFromInventory(oid,basem):
    myresult = sendGetRequest("SELECT "+basem+" FROM item WHERE id = '"+str(oid)+"'")
    if len(myresult)>=0:
        for item in myresult:
            if int(item[0])>0:
                removeOneItem(oid,basem)
                return True
    return False

def removeOneItem(oid,basem):
    sendRequest("UPDATE item SET "+basem+"="+basem+" - 1 WHERE id = '"+str(oid)+"'")

def getInventory(oid):
    return sendGetRequest("SELECT small, medium, large FROM item WHERE id = '"+str(oid)+"'")

def getFullInventory(oid):
    return sendGetRequest("SELECT small, medium, large, tfive, tsix, modik FROM item WHERE id = '"+str(oid)+"'")

def addBoxToBase(oid, basem):
    sendRequest("UPDATE item SET "+basem+"="+basem+" + 1 WHERE id = '"+str(oid)+"'")

def addItemToBase(oid, basem):
    sendRequest("UPDATE item SET "+basem+"="+basem +" + 1 WHERE id = '"+str(oid)+"'")

def setBoxWith(oid, basem, amount):
    sendRequest("INSERT INTO item (id, "+basem+") VALUES ('"+str(oid)+"',"+str(amount)+")")

def openBox(oid,basem,amount,prem):
    sendRequest("UPDATE item SET "+basem+"="+str(amount-1)+" WHERE id = '"+str(oid)+"'")
    maxR = 100.0
    if prem is True:
        maxR -= 25.0
    rnd_num = random.uniform(0.0,maxR)
    newbase = "-"
    result = "-"
    if basem=="small":
        if rnd_num<=1:
            result = "Комплект Т6 "+gem_complects[1]
            newbase = "tsix"
        elif rnd_num<=2:
            result = "Модик 2-4 "+gem_complects[2]
            newbase = "modik"
        elif rnd_num<=3:
            result = "<:bumaga:910831599631888404>"
        elif rnd_num<=28:
            result = "Комплект Т5 "+gem_complects[0]
            newbase = "tfive"
    elif basem=="medium":
        if rnd_num<=3:
            result = "Комплект Т6 "+gem_complects[1]
            newbase = "tsix"
        elif rnd_num<=6:
            result = "Модик 2-4 "+gem_complects[2]
            newbase = "modik"
        elif rnd_num<=7:
            result = "<:bumaga:910831599631888404>"
        elif rnd_num<=57:
            result = "Комплект Т5 "+gem_complects[0]
            newbase = "tfive"
    elif basem=="large":
        if rnd_num<=10:
            result = "Комплект Т6 "+gem_complects[1]
            newbase = "tsix"
        elif rnd_num<=20:
            result = "Модик 2-4 "+gem_complects[2]
            newbase = "modik"
        elif rnd_num<=21:
            result = "<:bumaga:910831599631888404>"
        else :
            result = "Комплект Т5 "+gem_complects[0]
            newbase = "tfive"
    if newbase!="-":
        addItemToBase(oid,newbase)
    return result 

def updateTop(item,mod,owner,id):
    sendRequest("UPDATE top SET item='"+item+"',modif="+str(mod)+",name='"+owner+"',amount=1 WHERE id = '"+str(id)+"'")

def addAmountToTop(item,mod,owner,id,amount):
    sendRequest("UPDATE top SET item='"+item+"',modif="+str(mod)+",name='"+owner+"',amount="+str(amount+1)+" WHERE id = '"+str(id)+"'")

def setNewTop(item,mod,owner,id):
    sendRequest("INSERT INTO top (item, modif, name, id) VALUES ('"+item+"',"+str(mod)+",'"+owner+"','"+str(id)+"')")

def saveTopToDB(bitem,bmod,bowner,id):
    myresult = sendGetRequest("SELECT item, name, modif, amount FROM top WHERE id = '"+str(id)+"'")
    if len(myresult)>0:
        for item, name, modif, amount in myresult:
            if bmod>modif:
                updateTop(bitem,bmod,bowner,id)
            elif bmod==modif:
                addAmountToTop(bitem,bmod,bowner,id,amount)
    else:
        setNewTop(bitem,bmod,bowner,id)

def isCD(ctx):
    id = str(ctx.message.author.id)
    result = "-"
    myresult = sendGetRequest("SELECT time FROM cd WHERE id = '"+id+"'")
    currentTime = int(time.time())
    if len(myresult)>0:
        for timet in myresult:
            idTime = int(timet[0])
            if idTime>=currentTime:
                return str(idTime-currentTime)
    return result

def saveCd(id,prem):
    myresult = sendGetRequest("SELECT time FROM cd WHERE id = '"+str(id)+"'")
    if len(myresult)>0:
        updateCd(id,prem)
    else:
        saveNewCd(id,prem)

def updateCd(id,prem):
    currentTime = int(time.time()) + 600
    if prem is True:
        currentTime -= 200
    sendRequest("UPDATE cd SET time="+str(currentTime)+" WHERE id = '"+str(id)+"'")

def saveNewCd(id,prem):
    currentTime = int(time.time()) + 600
    if prem is True:
        currentTime -= 200
    sendRequest("INSERT INTO cd(id, time) VALUES('"+str(id)+"',"+str(currentTime)+")")

def storeItem(tp,owner,item,owid):
    sendRequest("INSERT INTO stash(type,item,owner,oid) VALUES('"+tp+"','"+item+"','"+owner+"','"+str(owid)+"')")

def getItemsInBank(tp):
    myresult = sendGetRequest("SELECT item, owner FROM stash WHERE type = '"+tp+"'")
    return myresult

def getOwnItemsInBank(id):
    myresult = sendGetRequest("SELECT id, item FROM stash WHERE oid = '"+str(id)+"'")
    return myresult

def getSpecialItem(id):
    myresult = sendGetRequest("SELECT item, oid FROM stash WHERE id = "+id)
    return myresult

def removeItemFromBank(id):
    sendRequest("DELETE FROM stash WHERE id = "+id)