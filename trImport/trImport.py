


# trImport.py



# -----------------------------------------------------------------
# system

import os
import time
import datetime as dt # 현재시간 출력
import tracemalloc # 메모리 할당 추적
tracemalloc.start()

import sys
#trImportRoute = "/home/djlim/djlim/web/trImport/trImport.py"
#sys.path.append(trImportRoute) # 무조건 절대경로로

# -----------------------------------------------------------------
# web sockte

import asyncio      # 웹 소켓 모듈을 선언 
import websockets   # 클라이언트 접속이 되면 호출
import json # json 형식으로 웹소켓 데이터 송수신 하기 위한 모듈

# -----------------------------------------------------------------
# database 

from mysqlInfor import *
db = dbLink()

# -----------------------------------------------------------------
# telegram bot

from telegramBotInfor import *
from telegram import *
from telegram.ext import *

COMMAND_START_CODE = "@/"

bot = Bot(token)
updater = Updater(token = token, use_context = True)
dispatcher = updater.dispatcher

#------------------------------------------------------------
# google trans 객체 생성

from googletrans import Translator

translator = Translator()
INDEX_ALPHA = 0
INDEX_NAME = 1
INDEX_TRANS_NAME = 2

#------------------------------------------------------------
# threading & queue

import threading
from queue import Queue

