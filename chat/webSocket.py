

# webSocket.py


#------------------------------------------------------------
# 모듈 사용하는거 한곳에 모아서 관리중

import sys
trImportRoute = "/home/djlim/djlim/web/trImport"
sys.path.append(trImportRoute) # 무조건 절대경로로
from trImport import *

#------------------------------------------------------------
# 스레드 클래스

class Worker(threading.Thread):
    def __init__(self, name):
        super.__init__()
        self.name = name

msgQ = Queue()
msgNum = {}


# -----------------------------------------------------------------
# 서버 닫았다가 열면 텔레그램 정보 초기화

sqlStr = "UPDATE user SET telegramChatId=null"
db.dbRenew(sqlStr)

# -----------------------------------------------------------------

def insertDB(chatId, number, userId, data, original, alpha, date):
    sqlStr = "INSERT INTO message(chatId, number, userId, data, original, alpha, date) "
    sqlStr += ("VALUES("+
        "'"+str(chatId)+"',"
        "'"+str(number)+"',"
        "'"+str(userId)+"',"
        "'"+str(data)+"',"
        " "+str(original)+", "
        "'"+str(alpha)+"',"
        "'"+str(date)+"')")
    db.dbRenew(sqlStr)

def msgQueueThread(): # 처리할 메시지 큐 처리 스레드
    global msgQ
    global msgNum
    while True:
        msgOne=msgQ.get()
#        print(msgOne)
#        sendStr=msgOne['userId'] + ((20-len(msgOne['userId'])) * " ")
#        sendStr+=msgOnt['data']
#        msgOne['websocket'].send(msgOne)
#        asyncio.run(msgOne['websocket'].send(msgOne['msgStr']))
        dateNow = dt.datetime.now()
        dateStr = dateNow.strftime("%Y-%m-%d %H:%M:%S")

        dataJson = {
            'chatId' : str(msgOne['chatId']),
            'userId' : str(msgOne['userId']),
            'msgNum' : str(msgOne['msgNum']),
            'msgDate' : str(dateStr)
#            'msgStr' : msgOne['msgStr']
        }

        chatList=globals()["chatInfor_{}".format(msgOne['chatId'])]
        transDic={} # 같은 언어면 그대로 보내줌. 번역 거치치 않음
        for port in chatList: # 같은 채팅방 내에 있는 모든 연결 포트를 하나씩 불러옴
            userId = globals()["linkInfor_{}".format(str(port))].getUserId() # 해당 포트의 사용자 ID반환

            sqlStr = "SELECT languageAlpha FROM user WHERE id='"+str(userId)+"'" # 해당 사용자의 번역 alphaCode 추출
            alphaCode = db.dbFetchOneWord(sqlStr)

            if (alphaCode in transDic.keys()) == False:
                result = translator.translate(str(msgOne['msgStr']), dest=alphaCode) # 해당 언어로 번역
                dataJson['msgStr'] = str(result.text)
                transDic[alphaCode] = str(result.text) # 언어 번역한 딕셔너리에 추가
                insertDB(msgOne['chatId'], msgOne['msgNum'], msgOne['userId'], result.text, 'false', result.dest, dateStr)
            else:
                dataJson['msgStr'] = str(transDic[alphaCode])

            sendJson = json.dumps(dataJson)
            asyncio.run(globals()["linkInfor_{}".format(port)].getWebsocket().send(sendJson)) # 해당 포트에 메시지 전송

        sqlStr = "SELECT user FROM chatLink WHERE chatId='"+msgOne['chatId']+"'" # 채팅방에 있는 유저id모두 추출
        userList = db.dbFetchAll(sqlStr)
        sqlStr = "SELECT roomName FROM chatRoom WHERE chatid='"+str(msgOne['chatId'])+"'" # 해당 채팅방의 이름을 추출
        roomName = db.dbFetchOneWord(sqlStr)
#        print(userList)

        for inUserId in userList:
            sqlStr = "SELECT id, telegramChatId FROM user WHERE id='"+str(inUserId[0])+"'" # 해당 사용자의 텔레그램 채팅 id 추출
            tlChatInfor = db.dbFetchOne(sqlStr)
#            print(tlChatInfor)
            if tlChatInfor[1] != None: # 해당 사용자의 텔레그램 연결이 있다면
                if tlChatInfor[0] != str(msgOne['userId']): # 자신이 보낸 메시지가 아니면
                    tlClass = globals()["telegramInfor_{}".format(tlChatInfor[1])] # 텔레그램 연결확인 및 객체 생성
#                    print(tlClass.getUserId())
                    tlClass.sendMsg("["+roomName+"]방에서 새로운 메시지를 확인했습니다!")

        del transDic
        insertDB(msgOne['chatId'], msgOne['msgNum'], msgOne['userId'], msgOne['msgStr'], 'true', result.dest, dateStr)
#        print(sendJson)
#        asyncio.run(msgOne['websocket'].send(sendJson))

msgQueueThreadTd = threading.Thread(target=msgQueueThread, daemon=True)
msgQueueThreadTd.start()

class ChatUser: # 채팅방 유저 정보 클래스
    def __init__(self, chatId, userId, port):
        self.chatId = chatId # 채팅방 ID
        self.userId = userId # 사용자 ID
        self.port = port # 웹소켓 연결된 포트
    def getChatId(self):
        return self.chatId
    def getUserId(self):
        return self.userId
    def getUserPort(self):
        return self.port

class ChatRoom: # 채팅방 정보 클래스.
    global msgQ
    global msgNum
    def __init__(self, chatId, userId, websocket): # 초기화
        self.chatId=chatId # 채팅방 ID
        self.userId=userId # 채팅방 ID
        self.websocket=websocket # 웹소켓 객체
        if (self.chatId in msgNum) == False:
            msgNum[self.chatId] = 0
#        self.msgNum=0 # 채팅방의 메시지 마지막 번호
    def setMsgNum(self, num): # 메시지 마지막 번호 설정
#        self.msgNum = num
        msgNum[self.chatId] = num
    def getMsgNum(self): # 메시지 마지막 번호 반환
#        return self.msgNum
        return msgNum[self.chatId]
    def getUserId(self): # 사용자ID 반환
        return self.userId
    def upMsgNum(self): # 메시지 마지막 번호 ++
#        self.msgNum += 1
        msgNum[self.chatId] += 1
    def putQueue(self, userId, data): # 메시지 큐에 메시지 삽입
        self.upMsgNum()
        msgDic = {
            'chatId' : self.chatId, # 메시지의 소속 채팅방ID
            'websocket' : self.websocket, # 웹소켓 객체
            'userId' : userId, # 메시지 보낸 사용자의 ID
            'msgNum' : msgNum[self.chatId], # 메시지 번호
            'msgStr' : data # 메시지 내용
        }
#        print(msgDic)
        msgQ.put(msgDic) # 정보를 담은 딕셔너리 큐에 삽입
        del msgDic # 정보를 넘겼으니 해당 딕셔너리 삭제
    def getQueue(self):
        return self.msgQueue.get()
    def getWebsocket(self):
        return self.websocket

class tlChatRoom: # 텔레그램 채팅방 정보
    def __init__(self, update, context):
        self.update = update # update object
        self.context = context # context object
        self.userId = None # user id => 웹에서 회원가입한 id. 텔레그램과 연결하기 위한

    def setUpdate(self, update): # update 재설정
        self.update = update
    def setContext(self, context): # context 재설정
        self.context = context
    def setUserId(self, userId): # context 재설정
        self.userId = userId

    def getUpdate(self): # update 반환
        return self.update
    def getContext(self): # context 반환
        return self.context
    def getUserId(self): # userId 반환
        return self.userId
    def getChatId(self): # chatId 반환
        return self.update.effective_chat.id
    def getMessage(self): # massage 반환
        return self.update.message
    def getFname(self): # first name 반환
        return self.effective_chat.first_name
    def getLname(self): # last name 반환
        return self.effective_chat.last_name

    def sendMsg(self, msgStr):
        bot.sendMessage(chat_id=self.getChatId(), text=msgStr)
    def sendEcho(self):
        bot.sendMessage(chat_id=self.getChatId(), text=self.getMessage().text)
    def sendTransEcho(self):
        sqlStr = "SELECT languageAlpha FROM user WHERE id='"+str(self.userId)+"'" # 해당 사용자의 번역 alphaCode 추출
        alphaCode = db.dbFetchOneWord(sqlStr)
        result = translator.translate(str(self.getMessage().text), dest=alphaCode) # 해당 언어로 번역
        bot.sendMessage(chat_id=self.getChatId(), text=result.text)


def echoThread(update, context): # 텔레그램 채팅 감지시 도는 스레드
    try:
        globals()["telegramInfor_{}".format(update.effective_chat.id)].setUpdate(update) # 해당 객체있으면 update갱신,  없으면 예외처리로 만듦
    except:
        globals()["telegramInfor_{}".format(update.effective_chat.id)] = tlChatRoom(update, context)# 텔레그램 채팅방 모아둔 딕셔너리

    tlClass = globals()["telegramInfor_{}".format(update.effective_chat.id)]

    if(tlClass.getMessage().text[0] != '@'): # 커멘드 명령어인지 여부. 아닌경우가 많아서 else로 내림
        if(tlClass.getUserId() != None): # 텔레그램과 웹과 DB를 이용해서 연결되지 않았다면
#            tlClass.sendEcho()
            tlClass.sendTransEcho() # 번역 후 echo back
        else:
            tlClass.sendMsg("아직 로그인하지 않으셨습니다! \n @ID PASSWORD \n 형식으로 입력해 주세요.");
    else:
        commandTmp = tlClass.getMessage().text[1:]
        commandArray = commandTmp.split()
        if(tlClass.getUserId() != None): # 로그인 여부에 따라 명령어 권한이 다름. 
            tlClass.sendEcho() # 그냥 echo back
        else:
            if(len(commandArray) == 2):
                sqlStr = "SELECT id, AES_DECRYPT(unhex(password), 'D') FROM user WHERE id='"+str(commandArray[0])+"'"
                sqlCount = db.dbFetchOne(sqlStr)
                if sqlCount == None:
                    tlClass.sendMsg("입력하신 정보는 존재하지 않습니다!")
                else:
                    if str(sqlCount[1])[2:-1] != str(commandArray[1]):
                        tlClass.sendMsg("비밀번호가 틀렸습니다.")
                    else:
                        tlClass.sendMsg("정보가 확인되었습니다.")
                        tlClass.setUserId(commandArray[0])
                        sqlStr = "UPDATE user SET telegramChatId='"+str(tlClass.getChatId())+"' WHERE id='"+str(commandArray[0])+"'"
                        sqlCount = db.dbRenew(sqlStr)
                    
            else:
                tlClass.sendMsg("형식에 맞춰서 다시 입력해주세요!")
#    print(tlClass.getMessage().text)


def echo(update, context): # 이벤트 발생시 스레드 시작
    t = threading.Thread(target=echoThread, args=(update, context))
    t.start()

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)
updater.start_polling()

async def accept(websocket, path):
#    global msgQ
    data = await websocket.recv() # 첫번째로 사용자 정보를 받기위해 연결 후 한번만 실행하는 코드
    dataArr = data.split(',') # 처음으로 받은 데이터 채팅방ID, 사용자ID
    chatInfor = ChatUser(dataArr[0], dataArr[1], websocket.remote_address[1]) # 사용자 객체 생성. 채팅방ID, 사용자ID, 웹소켓 포트

    try: # 채팅방을 사용하는 사용자의 정보를 담은 딕셔너리
        globals()["linkInfor_{}".format(str(chatInfor.getUserPort()))].getMsgNum() # 해당 방연결  전역 클래스가 있다면 그냥 두고
    except:
        globals()["linkInfor_{}".format(str(chatInfor.getUserPort()))] = ChatRoom(chatInfor.getChatId(), chatInfor.getUserId(), websocket) # 없으면 만듦

    try: # 같은 채팅방에 속해있는 연결 정보를 담은 딕셔너리
        if (str(chatInfor.getUserPort()) in globals()["chatInfor_{}".format(chatInfor.getChatId())]) == False:
            globals()["chatInfor_{}".format(chatInfor.getChatId())].append(str(chatInfor.getUserPort())) # 같은 채팅방끼리 묶음
    except:
        globals()["chatInfor_{}".format(chatInfor.getChatId())] = [(str(chatInfor.getUserPort()))] # 같은 채팅방끼리 묶음

    print(globals()["chatInfor_{}".format(chatInfor.getChatId())])
    print("chatId / userId / port : " + chatInfor.getChatId() + " / " + chatInfor.getUserId() + " / " + str(chatInfor.getUserPort()) )
#    print(type(websocket.remote_address))
#    print(websocket.remote_address)

    sqlStr = "SELECT languageAlpha FROM user WHERE id='"+chatInfor.getUserId()+"'"
    userAlphaCode = db.dbFetchOneWord(sqlStr)
    sqlStr = "SELECT * FROM message WHERE chatId='"+chatInfor.getChatId()+"' AND alpha='"+userAlphaCode+"' AND original=false ORDER BY number"
    backupMsgList = db.dbFetchAll(sqlStr)
    sqlStr = "SELECT * FROM message WHERE chatId='"+chatInfor.getChatId()+"' AND original=true ORDER BY number"
    msgList = db.dbFetchAll(sqlStr)

    for listCount in range(len(msgList)):
        try: # 메시지 뽑아옴
            listData = backupMsgList[listCount]
            listMsgStr = str(listData[3])
        except: # 메시지 없으면 번역 안된것
            listData = msgList[listCount]
            trResult = translator.translate(str(listData[3]), dest=userAlphaCode)
            listMsgStr = str(trResult.text)
            insertDB(listData[0], listData[1], listData[2], listMsgStr, 'false', userAlphaCode, listData[6])

        backupMsgDic = {
            'chatId' : str(listData[0]), # 메시지의 소속 채팅방ID
            'userId' : str(listData[2]), # 메시지 보낸 사용자의 ID
            'msgNum' : str(listData[1]), # 메시지 번호
            'msgDate' : str(listData[6]),
            'msgStr' : str(listMsgStr) # 메시지 내용
        }
#        print(str(backupMsgDic))
        backupDendJson = json.dumps(backupMsgDic)
        await websocket.send(backupDendJson) # 해당 포트에 메시지 전송

        chatNum = globals()["linkInfor_{}".format(str(chatInfor.getUserPort()))].getMsgNum() # 현재 채팅방 msg번호
        backupChatNum = listData[1] # 메시지 번호
        if chatNum <= backupChatNum:
            globals()["linkInfor_{}".format(str(chatInfor.getUserPort()))].setMsgNum(backupChatNum)

    while True:
        try:
            data = await websocket.recv()
        except:
            print("["+str(chatInfor.getUserPort())+"] 연결 끊어짐.");
            globals()["chatInfor_{}".format(chatInfor.getChatId())].remove(str(chatInfor.getUserPort()))
#            print("["+str(globals()["chatInfor_{}".format(chatInfor.getChatId())])+"] 채팅방 모음.");
            del globals()["linkInfor_{}".format(chatInfor.getUserPort())]
            del chatInfor
            break

        sqlStr="INSERT INTO message(chatId, number, userId, data, original, date)"
#        print(chatInfor.getUserId() + " : " + data)
        globals()["linkInfor_{}".format(str(chatInfor.getUserPort()))].putQueue(chatInfor.getUserId(), data)
#        await websocket.send(data)

print("web socket server open!!")
#start_server = websockets.serve(accept, "192.168.219.8", 51954)
start_server = websockets.serve(accept, "192.168.0.50", 60002)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()



