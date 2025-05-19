from telegram.ext import Updater, CommandHandler
import telegram
import cv2
import threading
import time
import os
import requests
import urllib
import subprocess
import signal
import psutil
import datetime
from telegram_token import CHAT_ID

ChatID = CHAT_ID
g_updater = None

def check_internet(url = 'https://www.google.com/', timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        return True
    except:
        return False

def connection_watcher(bot, updater):
    connection_state = True
    while True:
        time.sleep(60)
        try:
            if not updater.running:
                connection_state = False

            if check_internet() and connection_state == False:
                with open("/home/akin/guvenlik/errorlog.txt", "a") as f:
                    f.write("Baglanti kesildi sunucu yeniden baslatiliyor!/n")
                    f.close()
                subprocess.Popen('systemctl restart guvenlik.service', shell=True)

        except Exception as e:
            ct = datetime.datetime.now()
            with open("/home/akin/guvenlik/errorlog.txt", "a") as f:
                f.write(str(ct) + ": " + str(e) +"\n")
                f.close()

def terminate_process():
    #g_updater.stop()
    pid = os.getpid()
    ThisSystem = psutil.Process(pid)
    ThisSystem.terminate()

def update_init(update, context):
    try:
        context.bot.send_message(chat_id=update.message.chat_id,text='init.py Aliniyor ...')
        r = requests.get('https://raw.githubusercontent.com/akinsezer26/PersonDetection_TelegramBot/master/update/init.py')
        context.bot.send_message(chat_id=update.message.chat_id,text="Dosya basariyla alindi")

        f = open('/home/akin/guvenlik/init_tmp.py','w')
        f.write(r.text)

        context.bot.send_message(chat_id=update.message.chat_id,text="Sunucu 1 dk icinde tekrar başlatılacaktır")

        subprocess.Popen('sleep 30 && cp -f /home/akin/guvenlik/init_tmp.py /home/akin/guvenlik/init.py', shell=True)
        subprocess.Popen('sleep 45 && rm -f /home/akin/guvenlik/init_tmp.py', shell=True)
        os.system("sudo shutdown -r +1")
        exit()
        #terminate_process()

    except Exception as error:
        context.bot.send_message(chat_id=update.message.chat_id,text=str(error)) 

def update_TelegramBot(update, context):
    try:
        context.bot.send_message(chat_id=update.message.chat_id,text='TelegramBot.py Aliniyor ...')
        r = requests.get('https://raw.githubusercontent.com/akinsezer26/PersonDetection_TelegramBot/master/update/TelegramBot.py')
        context.bot.send_message(chat_id=update.message.chat_id,text="Dosya basariyla alindi")

        f = open('/home/akin/guvenlik/TelegramBot_tmp.py','w')
        f.write(r.text)

        context.bot.send_message(chat_id=update.message.chat_id,text="Sunucu 1 dk icinde tekrar başlatılacaktır")

        subprocess.Popen('sleep 30 && cp -f /home/akin/guvenlik/TelegramBot_tmp.py /home/akin/guvenlik/TelegramBot.py', shell=True)
        subprocess.Popen('sleep 45 && rm -f /home/akin/guvenlik/TelegramBot_tmp.py', shell=True)
        os.system("sudo shutdown -r +1")

        #terminate_process()

    except Exception as error:
        context.bot.send_message(chat_id=update.message.chat_id,text=str(error))

def update_detector(update, context):
    try:
        context.bot.send_message(chat_id=update.message.chat_id,text='detector.py Aliniyor ...')
        r = requests.get('https://raw.githubusercontent.com/akinsezer26/PersonDetection_TelegramBot/master/update/detector.py')
        context.bot.send_message(chat_id=update.message.chat_id,text="Dosya basariyla alindi")

        f = open('/home/akin/guvenlik/detector_tmp.py','w')
        f.write(r.text)

        context.bot.send_message(chat_id=update.message.chat_id,text="Sunucu 1 dk icinde tekrar başlatılacaktır")

        subprocess.Popen('sleep 30 && cp -f /home/akin/guvenlik/detector_tmp.py /home/akin/guvenlik/detector.py', shell=True)
        subprocess.Popen('sleep 45 && rm -f /home/akin/guvenlik/detector_tmp.py', shell=True)
        os.system("sudo shutdown -r +1")

        #terminate_process()

    except Exception as error:
        context.bot.send_message(chat_id=update.message.chat_id,text=str(error)) 

def update_model(update, context):
    try:
        context.bot.send_message(chat_id=update.message.chat_id,text='model Aliniyor ...')
        
        model = urllib.request.urlopen("https://raw.githubusercontent.com/akinsezer26/PersonDetection_TelegramBot/master/update/yolov3-tiny.weights")
        context.bot.send_message(chat_id=update.message.chat_id,text="Dosya basariyla alindi")

        with open('/home/pi/darknet/yolov3-tiny_tmp.weights','wb') as output:
            output.write(model.read())

        context.bot.send_message(chat_id=update.message.chat_id,text="Sunucu 1 dk icinde tekrar başlatılacaktır")

        subprocess.Popen('sleep 30 && cp -f /home/akin/guvenlik/yolov3-tiny_tmp.weights /home/akin/guvenlik/yolov3-tiny.weights', shell=True)
        subprocess.Popen('sleep 45 && rm -f /home/akin/guvenlik/yolov3-tiny_tmp.weights', shell=True)
        os.system("sudo shutdown -r +1")

        terminate_process()

    except Exception as error:
        context.bot.send_message(chat_id=update.message.chat_id,text=str(error))

def update(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text='/update_init\n/update_TelegramBot\n/update_detector\n/update_model\n')

def get_init(update, context):
    context.bot.sendDocument(chat_id=update.message.chat_id, document = open('/home/akin/guvenlik/init.py','rb'), filename = 'init.py')

def get_Telegram_Bot(update, context):
    context.bot.sendDocument(chat_id=update.message.chat_id, document = open('/home/akin/guvenlik/TelegramBot.py','rb'), filename = 'TelegramBot.py')

def get_detector(update, context):
    context.bot.sendDocument(chat_id=update.message.chat_id, document = open('/home/akin/guvenlik/detector.py','rb'), filename = 'detector.py')

def start_server():
    bot = telegram.Bot('1330874191:AAFdhp7SHM3T21umc6zz4ZdWI34iWlh_7fQ')
    updater = Updater('1330874191:AAFdhp7SHM3T21umc6zz4ZdWI34iWlh_7fQ',use_context=True)

    bot.send_message(chat_id=ChatID,text="Sunucu Baslatildi")

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('update', update))
    dp.add_handler(CommandHandler('update_init', update_init))
    dp.add_handler(CommandHandler('update_TelegramBot', update_TelegramBot))
    dp.add_handler(CommandHandler('update_detector', update_detector))
    dp.add_handler(CommandHandler('update_model', update_model))
    dp.add_handler(CommandHandler('get_init', get_init))
    dp.add_handler(CommandHandler('get_Telegram_Bot', get_Telegram_Bot))
    dp.add_handler(CommandHandler('get_detector', get_detector))

    return bot, updater

def start_telegram_bot(bot, updater):
    try:
        from TelegramBot import server
        server(bot, updater, ChatID)

    except Exception as error:
        bot.send_message(chat_id=ChatID,text=str(error))
        updater.start_polling()

if __name__ == '__main__':
    try:
        bot, updater = start_server()
        g_updater = updater
        threading.Thread(target=connection_watcher, args=(bot, updater), daemon=True).start()
        start_telegram_bot(bot, updater)
        
    except Exception as e:
        ct = datetime.datetime.now()
        with open("/home/akin/guvenlik/errorlog.txt", "a") as f:
            f.write(str(ct) + ": " + str(e) +"\n")
            f.close()
