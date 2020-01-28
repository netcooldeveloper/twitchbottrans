#
#############################
# Twitch Chat Translator bot
# 
# TCP Soket edition
#############################
from googletrans import Translator
'''
https://pypi.org/project/googletrans/
  by ssut
'''

import json
import socket
import string

DEBUG_MODE = False

def Send_message(message):
    sendmsg = "PRIVMSG #" + CHANNEL + " : " + message
    Socket_send(sendmsg)

def Socket_send(message):
    if (DEBUG_MODE):
        print("send << " + message)
    s.send((message+"\r\n").encode())

# Config load : format JSON
f = open("config.json")
json_data = json.load(f)
f.close

# Twitch IRC Info
HOST = json_data['TwitchIrcServerInfo']['address']
PORT = json_data['TwitchIrcServerInfo']['port']

# Twitch Bot Info
NICK = json_data['BotInfo']['TwitchAccountID']
PASS = json_data['BotInfo']['oauth']

# Twitch TV Channel Info
CHANNEL = json_data['TransTV']['TwitchAccountID']

# Initialize
readbuffer = ""

# Soket 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Twitch IRC server Connect
s.connect((HOST,PORT))

# Authentication
sendmsg = "PASS " + PASS
Socket_send(sendmsg)

sendmsg = "NICK " + NICK
Socket_send(sendmsg)

# Twich Channel Change
sendmsg = "JOIN #" + CHANNEL
Socket_send(sendmsg)

# Google Tranlator 
gt = Translator()

flagEndMsg = 0

while True:
    # IRC Server -> DATA -> RECV
    readbuffer = readbuffer + (s.recv(1024)).decode()
    temp = readbuffer.split("\n")

    readbuffer = temp.pop()

    for line in temp :
        if(DEBUG_MODE):
            print("recv >> " + line)

        ports = line.split(":")

        if ("PING" in ports[0]):
            sendmsg = "PONG %s" % ports[1]
            Socket_send(sendmsg)
            continue

        if "QUIT" not in ports[1] and "JOIN" not in ports[1] and "PORT" not in ports[1] :
            try:
                message = ports[2][:len(ports[2]) - 1]
            except:
                message = ""

            usernamesplit = ports[1].split("!")
            username = usernamesplit[0]

            if (message in "End of /NAMES list"):
                flagEndMsg = 1
                continue

            if (flagEndMsg == 1):
                fromlang = ""
                try:
                    fromlang = gt.detect(message).lang
                except:
                    fromlang =""
                
                if (fromlang in json_data['TranslatorInfo']['toLanguage']):
                    tolang = "en"
                else:
                    tolang = json_data['TranslatorInfo']['toLanguage']

                tranText = gt.translate(message, dest=tolang).text

                Send_message(tranText + "  <<(" + username + ")")
