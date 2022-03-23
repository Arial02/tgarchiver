from bs4 import BeautifulSoup as bs
from time import*
import requests
import datetime
from random import randint
import os
import zipfile
import string

class Del:
  def __init__(self, keep=string.digits):
    self.comp = dict((ord(c),c) for c in keep)
  def __getitem__(self, k):
    return self.comp.get(k)

DD = Del()

def zipdir(path, zipfile1):
    for root, dirs, files in os.walk(path):
        for file in files:
            zipfile1.write(os.path.join(root,file))

def torange(a):
    if a<0:return 0
    else:return a

def delnewstr(s):
    i=0
    while True:
        if i>=len(s):break
        if (s[i]=='\n' or s[i]==' ') and (s[torange(i-1)]=='\n' or s[torange(i-1)]==' '):
            s=s[:i]+s[torange(i+1):]
            continue
        i+=1
    return s

class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
        self.https_proxy="https://92.39.55.186:48537"
        self.proxies={"https":self.https_proxy}

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params) #proxy
        result_json = resp.json()['result']
        return result_json

    def get_file(self, doc, offset=None, timeout=30):
        loader=self.api_url[:25]+'file/'+self.api_url[25:]
        doc_id=doc['file_id']
        method = 'getFile?file_id='
        params={'timeout': timeout, 'offset': offset}
        resp=requests.get(self.api_url+method+doc_id, params) #proxy
        res_json=resp.json()['result']
        file_path=res_json['file_path']
        sleep(2.0)
        file=requests.get(loader+file_path,params) #proxy
        return file.content


    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params) #proxy
        return resp

    def send_file(self, chat_id, file):
        method='sendDocument?chat_id={}'.format(chat_id)
        params = {'document':file}
        resp=requests.post(self.api_url+method, files=params) #proxy
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = None

        return last_update

archiv_bot = BotHandler('insert your token here')

def main():
    new_offset = None

    while True:
        archiv_bot.get_updates(new_offset)

        last_update = archiv_bot.get_last_update()

        if last_update==None:
            sleep(2.0)
            continue

        last_update_id = last_update['update_id']
        if('text' in last_update['message']):last_chat_text = last_update['message']['text']
        else:last_chat_text=None
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']
        if('document' in last_update['message']):last_chat_file = last_update['message']['document']
        else:last_chat_file=None
        classes=['message default clearfix','message default clearfix joined']

        if last_chat_text:
            print(datetime.datetime.now().time(),' '+last_chat_name+' just has used this command: '+last_chat_text)
            if last_chat_text.lower()=="/start":
                archiv_bot.send_message(last_chat_id,
                                   "Здравствуй, {}!\n".format(last_chat_name) +
                                   "Я могу скачать твою переписку тебе на устройство, как только ты меня об этом попросишь! Я молодец, правда же?\n" +
                                   "Как только ты скинешь мне html файл с экспортированной перепиской "
                                   "(через десктопную версию, три точки в правом верхнем углу чата, затем Export chat history или подобное), "
                                   "я разложу тебе его по txt файлам и отправлю архивом!\n" +
                                   "Кстати, я могу скачать по объёму и отправителю сообщений. Я ещё умный.\n" +
                                   "И скромный.\n"
                                   "Жми /help, если хочешь больше о командах."
                                    )
            elif last_chat_text.lower()=='/ping':
                archiv_bot.send_message(last_chat_id,'pong!')
            elif last_chat_text.lower()[:8]=='/classes':
                if len(last_chat_text.lower())>9:
                    s=last_chat_text.lower()[10:]
                    classes=s.split(', ')
                    archiv_bot.send_message(last_chat_id, 'Done!')
                else:
                    classes=['message default clearfix','message default clearfix joined']
                    archiv_bot.send_message(last_chat_id, 'Done!')
            elif last_chat_text.lower()[:7]=='/search':
                answer=''
                s=last_chat_text.lower()
                search_chat_id=s[8:].split(' ')[0]
                search_chat_text=s[8+len(search_chat_id)+1:]
                for root, dirs, filenames in os.walk('./chats/chat{}'.format(search_chat_id)):
                    for f in filenames:
                        if open(root+'/'+f,'r',encoding='utf-8').read().lower().find(search_chat_text)!=-1 and f!='fhtml.html':answer+='{},\n'.format(f.translate(DD))
                archiv_bot.send_message(last_chat_id, answer)
            elif last_chat_text.lower()=='/help':
                archiv_bot.send_message(last_chat_id,'/start - приветствие, суть бота;\n'
                                                     '/ping - pong!;\n'
                                                     '/classes: qq, abvgd, ork - стоит менять, только если вы шарите. '
                                                     'Это установка классов для поиска и архивирования по ним в хтмле. '
                                                     'Для установки дефолтных классов переписки Телеги введите "classes:". '
                                                     '(Если что, дефолтные называются message default clearfix, message default clearfix joined)\n'
                                                     '/search 12345 Hello, David! - поиск по переписке под номером таким-то '
                                                     '(вам присылается архив с названием чат+номер, это тот самый номер) такой-то строки. '
                                                     'Регистр неважен.\n'
                                                     '/help - объяснения излишни...\n'
                                                     'Ну, а если придёт файл хтмл, то я его разберу и сархивирую! Вперёд!')
            else:
                archiv_bot.send_message(last_chat_id,
                                        "Что? Что ты от меня хочешь, юзер? Жми /start и погнали!")
        if last_chat_file!=None:
            print(datetime.datetime.now().time(),' '+last_chat_name+' just has sent us the file! '+last_chat_file['file_name'])
            t1=time()
            number=randint(0,100000)
            os.makedirs('./chats/chat{}'.format(str(number)))
            # coding: utf8
            html=open('./chats/chat{}/fhtml.html'.format(number),'w',encoding='utf-8')
            html.write(archiv_bot.get_file(last_chat_file).decode('utf-8'))
            html.close()
            html=open('./chats/chat{}/fhtml.html'.format(number),'r',encoding='utf-8')
            soup=bs(html)
            count=0
            for msg in soup.find_all('div', {'class':classes}):
                f=open('./chats/chat{}/msg_{}.txt'.format(number,count),'w',encoding='utf-8')
                f.write(delnewstr(msg.getText()))
                f.close()
                count+=1
            html.close()
            zipf=zipfile.ZipFile('./chats/chat{}.zip'.format(str(number)), 'w', zipfile.ZIP_DEFLATED)
            zipdir('./chats/chat{}'.format(str(number)),zipf)
            zipf.close()
            zipf=open('./chats/chat{}.zip'.format(str(number)), 'rb')
            archiv_bot.send_file(last_chat_id, zipf)
            zipf.close()
            t2=time()
            archiv_bot.send_message(last_chat_id, 'Я обработал '+str(last_chat_file['file_size'])+' байт за '+str(int(t2-t1))+' секунд! :Р')


        new_offset = last_update_id + 1

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
