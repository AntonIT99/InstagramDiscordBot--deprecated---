#!/usr/bin/python

# DESCRIPTION:
# This script executes 2 actions:
# 1.) Monitors for new image posted in a instagram account.
# 2.) If found new image, a bot posts new instagram image in a discord channel.
# 3.) Repeat after set interval.

# REQUIREMENTS:
# - Python v3
# - Python module re, json, requests

import re
import json
import sys
import requests
import urllib.request
import os
import time
import discord
import threading
import datetime
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands
from threading import Thread

#from dotenv import load_dotenv

# USAGE:
# Environment Variables
# Set IG_USERNAME to username account you want to monitor. Example - ladygaga
# Set WEBHOOK_URL to Discord account webhook url. To know how, just Google: "how to create webhook discord".
# Set TIME_INTERVAL to the time in seconds in between each check for a new post. Example - 1.5, 600 (default=600)

os.environ['IG_USERNAME1'] = 'username1'
os.environ['IG_USERNAME2'] = 'username2'
os.environ['IG_USERNAME3'] = 'username3'
os.environ['WEBHOOK_URL'] = 'private_url'
os.environ['TIME_INTERVAL'] = '3600'
webhook = Webhook.from_url('private_url', adapter=RequestsWebhookAdapter())

INSTAGRAM_USERNAME1 = os.environ.get('IG_USERNAME1')
INSTAGRAM_USERNAME2 = os.environ.get('IG_USERNAME2')
INSTAGRAM_USERNAME3 = os.environ.get('IG_USERNAME3')

last_image1 = ""
last_image2 = ""
last_image3 = ""

#non-Webhook initialisation
#load_dotenv()
TOKEN = 'ODkzNDA1NTgzODI5NTA0MDcw.YVa-yQ.ENVt2lrTYj5-Z1p54hfYiIl9ypI'
#os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix="$")

def get_user_fullname(html):
    return html.json()["graphql"]["user"]["full_name"]


def get_total_photos(html):
    return int(html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["count"])


def get_last_publication_url(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["shortcode"]


def get_last_photo_url(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["display_url"]


def get_last_thumb_url(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["thumbnail_src"]


def get_description_photo(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]


def webhook_send_instagram(webhook_url, html, username):
    data = {}
    data["embeds"] = []
    embed = {}
    embed["color"] = 15467852
    embed["title"] = "Neuer Beitrag von @"+ str(username) +""
    embed["url"] = "https://www.instagram.com/p/" + \
        get_last_publication_url(html)+"/"
    embed["description"] = get_description_photo(html)
    embed["image"] = {"url":get_last_thumb_url(html)} # unmark to post bigger image
    embed["thumbnail"] = {"url": get_last_thumb_url(html)}
    data["embeds"].append(embed)
    result = requests.post(webhook_url, data=json.dumps(
        data), headers={"Content-Type": "application/json"})
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Image successfully posted in Discord, code {}.".format(
            result.status_code))


def get_instagram_html(username):
    headers = {
        "Host": "www.instagram.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
    }
    html = requests.get("https://www.instagram.com/" + str(username) + "/feed/?__a=1", headers=headers)
    return html


def mainWebhook():
    try:
        html1 = get_instagram_html(INSTAGRAM_USERNAME1)
        html2 = get_instagram_html(INSTAGRAM_USERNAME2)
        html3 = get_instagram_html(INSTAGRAM_USERNAME3)
        print("ID1:" + os.environ["LAST_IMAGE_ID1"])
        print("ID2:" + os.environ["LAST_IMAGE_ID2"])
        print("ID3:" + os.environ["LAST_IMAGE_ID3"])
        
        if(os.environ.get("LAST_IMAGE_ID1") == get_last_publication_url(html1)):
            print("SRC1: No new image to post in discord.")
        else:
            os.environ["LAST_IMAGE_ID1"] = get_last_publication_url(html1)
            last_image1 = get_last_publication_url(html1)
            print("SRC1: New image to post in discord.")
            webhook_send_instagram(os.environ.get('WEBHOOK_URL'), get_instagram_html(INSTAGRAM_USERNAME1), INSTAGRAM_USERNAME1)
            webhook.send("$SRC1:"+get_last_publication_url(html1))
            
        if(os.environ.get("LAST_IMAGE_ID2") == get_last_publication_url(html2)):
            print("SRC2: No new image to post in discord.")
        else:
            os.environ["LAST_IMAGE_ID2"] = get_last_publication_url(html2)
            last_image2 = get_last_publication_url(html2)
            print("SRC2: New image to post in discord.")
            webhook_send_instagram(os.environ.get('WEBHOOK_URL'), get_instagram_html(INSTAGRAM_USERNAME2), INSTAGRAM_USERNAME2)
            webhook.send("$SRC2:"+get_last_publication_url(html2))
            
        if(os.environ.get("LAST_IMAGE_ID3") == get_last_publication_url(html3)):
            print("SRC3: No new image to post in discord.")
        else:
            os.environ["LAST_IMAGE_ID3"] = get_last_publication_url(html3)
            last_image3 = get_last_publication_url(html3)
            print("SRC3: New image to post in discord.")
            webhook_send_instagram(os.environ.get('WEBHOOK_URL'), get_instagram_html(INSTAGRAM_USERNAME3), INSTAGRAM_USERNAME3)
            webhook.send("$SRC3:"+get_last_publication_url(html3))
        
    except Exception as e:
        print("Exception: ")
        print(e)
        
def runBot():
    client.run(TOKEN)

def runWebhook():
    if os.environ.get('IG_USERNAME1') != None and os.environ.get('WEBHOOK_URL') != None:
        time.sleep(float(5))
        os.environ["LAST_IMAGE_ID1"] = last_image1
        os.environ["LAST_IMAGE_ID2"] = last_image2
        os.environ["LAST_IMAGE_ID3"] = last_image3
        while True:
            mainWebhook()
            time.sleep(float(os.environ.get('TIME_INTERVAL') or 600))
    else:
        print('Please configure environment variables properly!')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    channel_id = 893398371656683520
    channel = client.get_channel(channel_id)
    last_message_src1 = None
    last_message_src2 = None
    last_message_src3 = None
    async for message in channel.history():
        if (message.webhook_id == 893399637224988672):
            if(message.content.startswith('$SRC1:')):
                if (last_message_src1 == None):
                    last_message_src1 = message
                if (message.created_at > last_message_src1.created_at):
                    last_message_src1 = message
                
            if(message.content.startswith('$SRC2:')):
                if (last_message_src2 == None):
                    last_message_src2 = message
                if (message.created_at > last_message_src2.created_at):
                    last_message_src2 = message  
                
            if(message.content.startswith('$SRC3:')):
                if (last_message_src3 == None):
                    last_message_src3 = message
                if (message.created_at > last_message_src3.created_at):
                    last_message_src3 = message
    global last_image1 
    last_image1 = last_message_src1.content[6:]
    global last_image2 
    last_image2 = last_message_src2.content[6:]
    global last_image3 
    last_image3 = last_message_src3.content[6:]
    print("Last publications loaded.")
    
@client.event
async def on_message(message):
    print(message.content)
    if (message.webhook_id == 893399637224988672):
            if(message.content.startswith('$SRC1:')):
                global last_image1 
                last_image1 = message.content[6:]
                print("Source 1 last publication updated")
                
            if(message.content.startswith('$SRC2:')):
                global last_image2 
                last_image2 = message.content[6:]
                print("Source 2 last publication updated")
                
            if(message.content.startswith('$SRC3:')):
                global last_image3 
                last_image3 = message.content[6:]
                print("Source 3 last publication updated")
    await client.process_commands(message)

@client.command()                
async def ping(ctx):
    print("Ping recieved.")
    await ctx.channel.send('pong')
    
@client.command()                
async def update(ctx):
    mainWebhook()

if __name__ == "__main__":
    thread = threading.Thread(target = runWebhook)
    thread.start()
    runBot()