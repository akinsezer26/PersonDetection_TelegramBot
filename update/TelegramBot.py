from telegram.ext import Updater, CommandHandler
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
import datetime
import RPi.GPIO as GPIO
import subprocess
import shlex
import requests
from telegram_token import CHAT_ID
from init import update, update_init, update_TelegramBot, update_detector, update_model, get_init, get_Telegram_Bot, get_detector

ChatID = CHAT_ID

delay = 3.0
isCalis = False
ServerStartDate = datetime.datetime.now()
interval = 0.5
isDc = False
dcStartH = 0
dcStartM = 0
dcEndH = 0
dcEndM = 0
global_bot = None
global_updater = None

GPIO.setmode(GPIO.BCM)
alarm = 18
GPIO.setup(alarm, GPIO.OUT)

def run_command(command: str) -> str:
    try:
        result = subprocess.run(
            ["/bin/bash", "-c", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode != 0:
            return f"Hata kodu {result.returncode}:\n{error or '(stderr boş)'}"
        return output or "(Hiçbir çıktı yok)"
    except Exception as e:
        return f"Beklenmeyen hata: {str(e)}"
        
def komutcalistir(update, context):
    text = update.message.text

    if text.startswith("/komutcalistir"):
        # Remove the command part and strip spaces
        command_part = text[len("/komutcalistir"):].strip()

        try:
            command_tokens = shlex.split(command_part)
            command = ' '.join(command_tokens)

            if not command:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Komut bulunamadı.")
                return

            # Send back the parsed command as debug
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Çalıştırılıyor: `{command}`", parse_mode='Markdown')

            result = run_command(command)
            context.bot.send_message(chat_id=update.effective_chat.id, text=result)

        except ValueError as e:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Komut ayrıştırma hatası: {e}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Komut tanınmadı.")

def alarmkapat(update, context):
    GPIO.output(alarm, GPIO.LOW)
    context.bot.send_message(chat_id=update.message.chat_id,text='Alarm kapatiliyor')

def alarmac(update, context):
    GPIO.output(alarm, GPIO.HIGH)
    context.bot.send_message(chat_id=update.message.chat_id,text='Alarm aciliyor')
    time.sleep(30)
    GPIO.output(alarm, GPIO.LOW)

def version(update, context):
    version = 'Jetson Nano Beta V1.0.0'
    context.bot.send_message(chat_id=update.message.chat_id,text=version)

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def calis(update, context):
    global isCalis
    isCalis = True

def calisma(update, context):
    global isCalis
    isCalis = False

def getCalis(update, context):
    duzC = ""
    if(isDc == True):
        duzC = "Acik\n"
    else:
        duzc = "Kapali\n"
    if(isCalis==True):
        str_ = "Calisiyor\n" + "Duzenli Calisma: " + duzC + str(dcStartH) +":"+ str(dcStartM) + " " + str(dcEndH) + ":" + str(dcEndM)
        context.bot.send_message(chat_id=update.message.chat_id,text=str_)
    else:
        str_ = "Calismiyor\n" + "Duzenli Calisma: " + duzC + str(dcStartH) +":"+ str(dcStartM) + " " + str(dcEndH) + ":" + str(dcEndM)
        context.bot.send_message(chat_id=update.message.chat_id,text=str_)

def yardim(update, context):
    str = "/versiyon\n"+"/sunucu_zamani\n"+"/calis\n"+"/calisma\n"+"/calisma_durumu\n"+"/sicaklik\n"+"/duzenli_calis\n"+"/duzenli_calisma\n"+"/duzenli_calismayi_ayarla\n"+"/alarmac\n"+"/alarmkapat\n"+"/gelismis\n"
    context.bot.send_message(chat_id=update.message.chat_id,text=str)

def developer(update, context):
    str = "/manual\n"+"/update\n"+"/sunucu_zamani\n"+"/calis\n"+"/calisma\n"+"/calisma_durumu\n"+"/set_delay\n"+"/set_interval\n"+"/get_delay\n"+"/get_interval\n"+"/sicaklik\n"+"/yeniden_baslat\n"+"/kapat\n"+"/rapor\n"+"/get_Telegram_Bot\n"+"/get_detector\n"+"/get_init\n"+"/get_error_log\n"+"/komutcalistir\n"
    context.bot.send_message(chat_id=update.message.chat_id,text=str)

def getDelay(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text=str(delay))

def getInterval(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text=str(interval))

def getErrorLog(update, context):
    context.bot.sendDocument(chat_id=update.message.chat_id, document = open('/home/akin/guvenlik/errorlog.txt','rb'), filename = 'hata_logu.txt')

def setDc(update, context):
    try:
        global dcStartH
        global dcStartM
        global dcEndH
        global dcEndM
        stra =  update.message.text.split(' ')[1]
        times = stra.split(':')

        start = datetime.time(int(times[0]),int(times[1]),0)
        end = datetime.time(int(times[2]),int(times[3]),0)

        dcStartH = times[0]
        dcStartM = times[1]
        dcEndH   = times[2]
        dcEndM   = times[3]
        context.bot.send_message(chat_id=update.message.chat_id,text="Atama Başarılı")
    except:
        context.bot.send_message(chat_id=update.message.chat_id,text="Geçersiz Komut")

def Dc(update, context):
    global isDc
    isDc = True

def Dcn(update, context):
    global isDc
    global isCalis
    isDc = False
    isCalis = False

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
    elapsedtime = datetime.datetime.now() - ServerStartDate
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
    os.system("sudo shutdown -h +1")
    global_updater.stop()

def restart(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text="Sunucu 1 dk icinde tekrar başlatılacaktır")
    os.system("sudo shutdown -r +1")
    global_updater.stop()

def manual(update, context):
    str = "delay    : Görüntü gönderme aralığı\ninterval : tespit etme aralığı"
    context.bot.send_message(chat_id=update.message.chat_id,text=str)

def is_connected(timeout=3):
    try:
        requests.get("https://www.google.com", timeout=timeout)
        return True
    except requests.RequestException:
        return False

def start_polling_thread():
    global global_bot
    global global_updater

    global_bot.send_message(chat_id=ChatID,text="Telegram Baglantisi Koptu Sunucu Tekrar Baslatildi")

    # dp = global_updater.dispatcher
    # dp.add_handler(CommandHandler('update', update))
    # dp.add_handler(CommandHandler('update_init', update_init))
    # dp.add_handler(CommandHandler('update_TelegramBot', update_TelegramBot))
    # dp.add_handler(CommandHandler('update_detector', update_detector))
    # dp.add_handler(CommandHandler('update_model', update_model))
    # dp.add_handler(CommandHandler('get_init', get_init))
    # dp.add_handler(CommandHandler('get_Telegram_Bot', get_Telegram_Bot))
    # dp.add_handler(CommandHandler('get_detector', get_detector))
    # dp.add_handler(CommandHandler('sunucu_zamani', getServerTime))
    # dp.add_handler(CommandHandler('calis', calis))
    # dp.add_handler(CommandHandler('calisma', calisma))
    # dp.add_handler(CommandHandler('calisma_durumu', getCalis))
    # dp.add_handler(CommandHandler('yardim', yardim))
    # dp.add_handler(CommandHandler('gelismis', developer))
    # dp.add_handler(CommandHandler('set_delay', setDelay))
    # dp.add_handler(CommandHandler('set_interval', setInterval))
    # dp.add_handler(CommandHandler('get_delay', getDelay))
    # dp.add_handler(CommandHandler('get_interval', getInterval))
    # dp.add_handler(CommandHandler('sicaklik', getTemp))
    # dp.add_handler(CommandHandler('kapat',shutdown))
    # dp.add_handler(CommandHandler('yeniden_baslat',restart))
    # dp.add_handler(CommandHandler('manual',manual))
    # dp.add_handler(CommandHandler('rapor',report))
    # dp.add_handler(CommandHandler('duzenli_calismayi_ayarla',setDc))
    # dp.add_handler(CommandHandler('duzenli_calis',Dc))
    # dp.add_handler(CommandHandler('duzenli_calisma',Dcn))
    # dp.add_handler(CommandHandler('versiyon',version))
    # dp.add_handler(CommandHandler('alarmac',alarmac))
    # dp.add_handler(CommandHandler('alarmkapat',alarmkapat))
    # dp.add_handler(CommandHandler('get_error_log',getErrorLog))
    # dp.add_handler(CommandHandler('komutcalistir',komutcalistir))

    global_updater.start_polling(timeout=90)

def error_handler(update, context):
    while True:
        if(is_connected()):
            thread = threading.Thread(target=start_polling_thread)
            thread.start()
            break
        else:
            pass
        time.sleep(60)

def server(bot, updater, ChatID):
    global global_bot
    global global_updater

    global_updater = updater
    global_bot = bot
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
    dp.add_handler(CommandHandler('duzenli_calismayi_ayarla',setDc))
    dp.add_handler(CommandHandler('duzenli_calis',Dc))
    dp.add_handler(CommandHandler('duzenli_calisma',Dcn))
    dp.add_handler(CommandHandler('versiyon',version))
    dp.add_handler(CommandHandler('alarmac',alarmac))
    dp.add_handler(CommandHandler('alarmkapat',alarmkapat))
    dp.add_handler(CommandHandler('get_error_log',getErrorLog))
    dp.add_handler(CommandHandler('komutcalistir',komutcalistir))
    dp.add_error_handler(error_handler)
    
    updater.start_polling(timeout=90)

    loop(bot, ChatID)

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

daily_report_flag = 0
def dailyReport(bot, chat_id):
    now = datetime.datetime.now()
    global daily_report_flag
    if(now.hour == 12 and now.minute == 30 and daily_report_flag == 0):
        bot.send_message(chat_id=chat_id, text='Sunucu Ayakta')
        daily_report_flag = 1
    elif(now.hour != 12 and now.minute != 30 and daily_report_flag == 1):
        daily_report_flag = 0

def loop(bot, ChatID):
    ch = yoloHandler(0)
    time.sleep(5)
    global lis
    cnt = 0
    global detectCount
    global totalError
    global totalBlackScreen
    global totalValid
    global totalPersonAvg
    global isCalis

    personCount = 0
    personSum = 0.0
    while(True):
        dt = datetime.datetime.now()
        dtH = dt.hour
        dtM = dt.minute

        dailyReport(bot, ChatID)

        start = datetime.time(int(dcStartH), int(dcStartM), 0)
        end = datetime.time(int(dcEndH), int(dcEndM), 0)

        if(isDc == True and time_in_range(start,end,datetime.time(dtH, dtM, 0)) ):
            isCalis = True
        elif(isDc == True and not time_in_range(start,end,datetime.time(dtH, dtM, 0))):
            isCalis = False

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

            currentProb = 0.0
            for element in output:
                if(element[0] == 'person'):
                    personCount+=1
                    currentProb = element[1]
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

                bot.send_photo(chat_id=ChatID, photo=bio, caption="Insan : %" + str(currentProb*100)[:4])
                time.sleep(float(delay))
        else:
            time.sleep(1)

if __name__ == '__main__':
    server()
    GPIO.cleanup()
