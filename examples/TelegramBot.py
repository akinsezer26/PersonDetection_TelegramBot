from telegram.ext import Updater, CommandHandler
from datetime import datetime
import telegram
import time
import numpy as np
import cv2
from detector import yoloHandler
from io import BytesIO
from PIL import Image
from subprocess import run
from subprocess import PIPE
import os
import threading

ChatID = #your Chat ID
delay = 3.0
isCalis = False
ServerStartDate = datetime.now()
interval = 0.5

def calis(update, context):
    global isCalis
    isCalis = True

def calisma(update, context):
    global isCalis
    isCalis = False

def getCalis(update, context):
    if(isCalis==True):
        context.bot.send_message(chat_id=update.message.chat_id,text="Calisiyor")
    else:
        context.bot.send_message(chat_id=update.message.chat_id,text="Calismiyor")

def yardim(update, context):
    str = "/sunucu_zamani\n"+"/calis\n"+"/calisma\n"+"/calisma_durumu\n"+"/sicaklik\n"+"/gelismis\n"
    context.bot.send_message(chat_id=update.message.chat_id,text=str)

def developer(update, context):
    str = "/manual\n"+"/sunucu_zamani\n"+"/calis\n"+"/calisma\n"+"/calisma_durumu\n"+"/set_delay\n"+"/set_interval\n"+"/get_delay\n"+"/get_interval\n"+"/sicaklik\n"+"/yeniden_baslat\n"+"/kapat\n"+"/rapor\n"
    context.bot.send_message(chat_id=update.message.chat_id,text=str)

def getDelay(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text=str(delay))

def getInterval(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text=str(interval))

def setDelay(update, context):
    try:
        global delay
        temp = update.message.text.split(' ')[1]
        temp = float(temp)
        delay = temp
        context.bot.send_message(chat_id=update.message.chat_id,text="delay "+str(delay)+"sn olarak atandı")
    except:
        context.bot.send_message(chat_id=update.message.chat_id,text="Geçersiz Komut")

def setInterval(update, context):
    try:
        global interval
        temp = update.message.text.split(' ')[1]
        temp = float(temp)
        interval = temp
        context.bot.send_message(chat_id=update.message.chat_id,text="interval "+str(interval)+"sn olarak atandı")
    except:
        context.bot.send_message(chat_id=update.message.chat_id,text="Geçersiz Komut")

def getServerTime(update, context):
    elapsedtime = datetime.now() - ServerStartDate
    elapsedtime_s = elapsedtime.total_seconds()
    hours = divmod(elapsedtime_s, 3600)[0]
    minutes = divmod(elapsedtime_s, 60)[0]%60
    seconds = divmod(elapsedtime.seconds, 60)[1]

    txt = str(round(hours))+' saat '+str(round(minutes))+' dakika '+str(round(seconds))+' saniye '
    context.bot.send_message(chat_id=update.message.chat_id,text=txt)

def getTemp(update, context):
    output = run("sensors", stdout=PIPE, stderr=PIPE)
    out = str(output)[55: -20: 1].replace(r'\xc2\xb0C','°C').replace(r'\n', '\n')
    context.bot.send_message(chat_id=update.message.chat_id,text=out)

import signal
import psutil
global_updater = None
def shutdown(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text="Sunucu 1 dk icinde kapanacaktır")
    global_updater.stop()
    os.system("sudo shutdown -h +1")
    pid = os.getpid()
    ThisSystem = psutil.Process(pid)
    ThisSystem.terminate()

def restart(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text="Sunucu 1 dk icinde tekrar başlatılacaktır")
    global_updater.stop()
    os.system("sudo shutdown -r +1")
    pid = os.getpid()
    ThisSystem = psutil.Process(pid)
    ThisSystem.terminate()

def cik(update, context):
    isCalis = False
    exit(0)

def manual(update, context):
    str = "delay    : Görüntü gönderme aralığı\ninterval : tespit etme aralığı"
    context.bot.send_message(chat_id=update.message.chat_id,text=str)

def server():
    bot = telegram.Bot('1330874191:AAHNYFZlEwDqToFMhByYlhNzotPNPczp5Dw')

    global global_updater

    global_updater = updater = Updater('1330874191:AAHNYFZlEwDqToFMhByYlhNzotPNPczp5Dw', use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('sunucu_zamani', getServerTime))
    dp.add_handler(CommandHandler('calis', calis))
    dp.add_handler(CommandHandler('calisma', calisma))
    dp.add_handler(CommandHandler('calisma_durumu', getCalis))
    dp.add_handler(CommandHandler('yardim', yardim))
    dp.add_handler(CommandHandler('gelismis', developer))
    dp.add_handler(CommandHandler('set_delay', setDelay))
    dp.add_handler(CommandHandler('set_interval', setInterval))
    dp.add_handler(CommandHandler('get_delay', getDelay))
    dp.add_handler(CommandHandler('get_interval', getInterval))
    dp.add_handler(CommandHandler('sicaklik', getTemp))
    dp.add_handler(CommandHandler('kapat',shutdown))
    dp.add_handler(CommandHandler('yeniden_baslat',restart))
    dp.add_handler(CommandHandler('manual',manual))
    dp.add_handler(CommandHandler('rapor',report))

    updater.start_polling()

    loop(bot)

    updater.idle()

detectCount = 0
totalError = 0
totalBlackScreen = 0
totalValid = 0
totalPersonAvg = 0.0

lis = [[] for i in range(25)]

def report(update , context):
    avg = 0.0
    sum = 0.0
    cnt = 0
    for row in lis:
        for element in row:
            if(element[0] == b'person'):
                cnt+=1
                sum+=element[1]
                ort=sum/cnt

    dc = ""
    if(detectCount<1000):
        dc = str(detectCount)
    elif(detectCount>1000 and detectCount<1000000):
        dc = str(detectCount)[:-3]+"k"
    else:
        dc = str(detectCount)[:-6]+"m"

    tv = ""
    if(totalValid<1000):
        tv = str(totalValid)
    elif(totalValid>1000 and totalValid<1000000):
        tv = str(totalValid)[:-3]+"k"
    else:
        tv = str(totalValid)[:-6]+"m"

    te = ""
    if(totalError<1000):
        te = str(totalError)
    elif(totalError>1000 and totalError<1000000):
        te = str(totalError)[:-3]+"k"
    else:
        te = str(totalError)[:-6]+"m"

    tbs = ""
    if(totalBlackScreen<1000):
        tbs = str(totalBlackScreen)
    elif(totalBlackScreen>1000 and totalBlackScreen<1000000):
        tbs = str(totalBlackScreen)[:-3]+"k"
    else:
        tbs = str(totalBlackScreen)[:-6]+"m"


    result = "+========= Rapor ========+\n"
    result +="Toplam Hesaplama= "+ dc+"\n"
    result +="Toplam Tespit         = "+ tv+"\n"
    result +="Toplam Hata            = "+ te +"\n"
    result +="Topl Siyah Ekran      = "+ tbs+"\n"
    result +="Ort İnsan Olasılık     = "+ "%"+str(totalPersonAvg*100)[:4]+"\n"
    result +="Son 25 İ. Olasılık     = "+ "%"+str(avg*100)[:4]+"\n"
    context.bot.send_message(chat_id=update.message.chat_id,text=result)

def loop(bot):

    ch = yoloHandler(0)
    time.sleep(5)
    bot.send_message(chat_id=ChatID,text="Sunucu Baslatildi")
    global lis
    cnt = 0
    global detectCount
    global totalError
    global totalBlackScreen
    global totalValid
    global totalPersonAvg

    personCount = 0
    personSum = 0.0
    while(True):
        if(isCalis == True):
            result,output=ch.yolo_detect(float(interval))
            if(cnt == 25):
                cnt = 0
            lis[cnt] = output
            #print(str(lis[cnt])+"\n")

            if(output == "Resim Siyah"):
                totalBlackScreen+=1
            elif(output == "Usb Takili Degil"):
                totalError+=1
            else:
                totalValid+=1

            for element in output:
                if(element[0] == b'person'):
                    personCount+=1
                    personSum+=element[1]
                    totalPersonAvg=personSum/personCount

            cnt+=1
            detectCount+=1

            if(result == True):
                pilImage = Image.fromarray( cv2.cvtColor(ch.DetectedImage, cv2.COLOR_BGR2RGB) )
                bio = BytesIO()
                bio.name = 'image.jpeg'
                pilImage.save(bio, 'JPEG')
                bio.seek(0)

                bot.send_photo(chat_id=ChatID, photo=bio, caption="Kameralar")
                time.sleep(float(delay))
        else:
            time.sleep(1)

if __name__ == '__main__':
    server()
