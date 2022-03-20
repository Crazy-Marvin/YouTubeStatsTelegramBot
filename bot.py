import os
import re
import requests
import telebot
import pyrebase
import requests
from datetime import date
from helper import stats
from datetime import timedelta
import google.oauth2.credentials
from telebot.types import InputMediaPhoto
from googleapiclient.discovery import build
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton


def video_id(url: str) -> str:    # https://stackoverflow.com/questions/4356538/
    regex = r"(?:http:|https:)*?\/\/(?:www\.|)" + \
            r"(?:youtube\.com|m\.youtube\.com|youtu\.|youtube-nocookie\.com).*" +\
            r"(?:v=|v%3D|v\/|(?:a|p)\/(?:a|u)\/\d.*\/|watch\?|vi(?:=|\/)" +\
            r"|\/embed\/|oembed\?|be\/|e\/)([^&?%#\/\n]*)"
    return regex_search(regex, url, group=1)

def regex_search(pattern: str, string: str, group: int):    # https://gist.github.com/987683cfbfcc8d800192da1e73adc486
    regex = re.compile(pattern)
    results = regex.search(string)
    if not results:                 
        return False
    return results.group(group)

def get_service(API_SERVICE_NAME, API_VERSION, creds):
    credentials = google.oauth2.credentials.Credentials(**creds)
    return build(
        API_SERVICE_NAME,
        API_VERSION,
        credentials=credentials
    )

def execute_api_request(client_library_function, **kwargs):
    return client_library_function(
        **kwargs).execute()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
CLIENT_SECRETS_FILE = r"google-credentials.json"

config = {

    "apiKey"            : os.getenv("apiKey"),
    "authDomain"        : os.getenv("authDomain"),
    "databaseURL"       : os.getenv("databaseURL"),
    "projectId"         : os.getenv("projectId"),
    "storageBucket"     : os.getenv("storageBucket"),
    "messagingSenderId" : os.getenv("messagingSenderId"),
    "appId"             : os.getenv("appId"),
    "measurementId"     : os.getenv("measurementId")
}

SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly', 
    'https://www.googleapis.com/auth/yt-analytics-monetary.readonly',
]

bot = telebot.TeleBot(TELEGRAM_API_KEY, parse_mode="HTML")
firebase = pyrebase.initialize_app(config)
database = firebase.database()

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "<b>WELCOME MESSAGE</b>",
    reply_markup=InlineKeyboardMarkup().add(*[
        InlineKeyboardButton(text="CHANNEL 🔔", callback_data="channel"),
        InlineKeyboardButton(text="VIDEOS 📽️", callback_data="videos"),
    ]))
    users = [user.key() for user in database.child("Users").get().each()]
    if str(message.chat.id) not in users:
        database.child("Users").child(message.chat.id).set({"videos":0, "video_ids":[], "sch":0})

def chk_vdo(url):
    if url.content_type != "text":
        bot.send_message(url.chat.id, "<b>INVALID URL! 😕</b>")
    else:
        id = video_id(url.text)
        if not id: 
            bot.send_message(url.chat.id, "<b>INVALID URL! 😕</b>")
        else:
            vdo = f"https://www.youtube.com/watch?v={id}"
            link = "https://www.googleapis.com/youtube/" +\
                "v3/" + f"videos?part=statistics&id={id}&key={YOUTUBE_API_KEY}"

            if requests.get(url=link).json()["pageInfo"]["totalResults"] == 0:
                bot.send_message(url.chat.id, "<b>INVALID URL! 😕</b>")
            else:
                bot.send_photo(url.chat.id, f"https://img.youtube.com/vi/{id}/0.jpg",
                caption=f"<b>OBTAINED VIDEO ID: <code>{id}</code>\n\
                    \nPRESS THE BUTTON TO CONFIRM THE VIDEO 👇🏻</b>",
                reply_markup=InlineKeyboardMarkup(row_width=2).add(*[
                    InlineKeyboardButton("CONFIRM 🟢", callback_data="confirm"),
                    InlineKeyboardButton("DECLINE 🔴", callback_data="decline"),
                    InlineKeyboardButton(text="CLICK TO WATCH THE VIDEO 🔗", url=vdo)]))

@bot.message_handler(commands=["stats"])
def statistics(message):
    vdo_count = database.child("Users").child(message.chat.id).child("videos").get().val()
    if vdo_count == 0:
        bot.send_message(message.chat.id, "<b>NO VIDEOS FOUND! 🙃</b>")
    else:
        vdo_set = list(set(database.child("Users").child(message.chat.id).child(
            "video_ids").order_by_key().get().val()))
        for vdo in vdo_set:
            stats(vdo, message.chat.id)

@bot.message_handler(commands=["channel"])
def channel(message):
    B1 = InlineKeyboardButton("VIEW ANALYTICS 📊", callback_data="analytics")
    verified = [user for user in database.child("OAuth2 Verified").get().val()]
    if str(message.chat.id) not in verified:
        B2 = InlineKeyboardButton("AUTHENTICATE NOW ✅", callback_data="authorize")
    else:
        B2 = InlineKeyboardButton("REVOKE ACCESS ❌", callback_data="revoke")
    bot.send_message(message.chat.id, "<b>What would you like to do? 👇🏻</b>",
    reply_markup=InlineKeyboardMarkup(row_width=1).add(*[B1, B2]))

def analytics(message):
    verified = [user for user in database.child("OAuth2 Verified").get().val()]
    if str(message.chat.id) not in verified:
        bot.send_message(message.chat.id,
        "<b>To use this feature, kindly authenticaate below 👇🏼</b>",
        reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(text="AUTHENTICATE NOW ✅",
            url=f"http://youtube-bot.crazymarvin.com/authorize/{message.chat.id}")))
    else:
        channel_id = database.child("Users").child(
            str(message.chat.id)).child("channel_id").get().val()
        logo_url = database.child("Users").child(
            str(message.chat.id)).child("logo_url").get().val()
        creds = dict(database.child("OAuth2 Verified").child(
            message.chat.id).get().val()) 
        youtube = get_service("youtube", "v3", creds)
        stats = execute_api_request(
            youtube.channels().list,
            id=channel_id,
            part='statistics')["items"][0]["statistics"]
        
        bot.send_photo(message.chat.id, photo=
    "AgACAgUAAxkBAAMNYfkZAAFB2Mee4aqlA2fOXlZIEtuAAAJyrjEbYRypV-Vo3tN12ti9AQADAgADeQADIwQ",
    caption="<b>Here are your latest channel analytics! 👇🏻</b>"),
        bot.send_photo(message.chat.id, logo_url, caption=
        f"<b>TOTAL VIEWS ➜ {stats['viewCount']}\n\
            \nTOTAL SUBSCRIBERS ➜ {stats['subscriberCount']}\n\
            \nTOTAL VIDEOS ➜ {stats['videoCount']}</b>")

        bot.send_message(message.chat.id, "<b>Here are your top videos 👇🏻</b>")

        analytics = get_service("youtubeAnalytics", "v2", creds)
        raw_data = execute_api_request(analytics.reports().query,
        ids='channel==MINE',
        startDate=str(date.today() - timedelta(days=14)),
        endDate=str(date.today()),
        dimensions='video',
        metrics='views,likes,dislikes,comments,estimatedMinutesWatched',
        maxResults=3,
        sort='-estimatedMinutesWatched')
        data = raw_data["rows"]
        if data == []:
            bot.send_photo(message.chat.id, 
    "AgACAgUAAxkBAAMdYgePHEINXRK7D4xHRyYFSz6I_4sAAgewMRsOeUBUu-auGtwNvY8BAAMCAAN4AAMjBA")
        else:
            for video in data:
                caption = f"<b>VIEWS ➜ {video[1]}\n\
                        \nLIKES ➜ {video[2]}\n\
                        \nDISLIKES ➜ {video[3]}\n\
                        \nCOMMENTS ➜ {video[-2]}\n\
                        \nESTIMATED WATCHTIME ➜ {video[-1]}</b>"
                try:
                    bot.send_photo(message.chat.id,
            f"https://img.youtube.com/vi/{video[0]}/0.jpg", caption=caption,
            reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(
        text="CLICK TO WATCH THE VIDEO 🔗", url=f"https://www.youtube.com/watch?v={video[0]}")))
                except:
                    bot.send_photo(message.chat.id, caption=caption, photo=
    "AgACAgUAAxkBAAMmYgeYiEMtgOZ1JZ3NzQABEz5gdRU0AAIesDEbDnlAVLO51_fSfeo7AQADAgADeAADIwQ",
    reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(
        text="CLICK TO WATCH THE VIDEO 🔗", url=f"https://www.youtube.com/watch?v={video[0]}")))

@bot.message_handler(commands=["videos"])
def videos(message):
    bot.send_message(message.chat.id, "<b>What would you like to do? 👇🏻</b>",
    reply_markup=InlineKeyboardMarkup(row_width=2).add(*[
        InlineKeyboardButton("ADD ➕", callback_data="add"),
        InlineKeyboardButton("DELETE ➖", callback_data="del"),
        InlineKeyboardButton("🔔 CHANGE SCHEDULE 🔔", callback_data="change"),])) 

@bot.message_handler(commands=["schedule"])
def schedule(message):
    bot.send_message(message.chat.id, "<b>Choose a schedule below 👇🏻</b>",
    reply_markup=InlineKeyboardMarkup().row(
        InlineKeyboardButton(text="NONE", callback_data="sch-0"),
        InlineKeyboardButton(text="DAILY", callback_data="sch-1"),
        InlineKeyboardButton(text="WEEKLY", callback_data="sch-2")))

@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, "<b>HELP INFORMATION</b>")

@bot.message_handler(commands=["contact"])
def contact(message):
    bot.send_message(message.chat.id, "<b>CONATCT INFORMATION</b>")

@bot.message_handler(commands=["feedback"])
def feedback(message):
    bot.send_message(message.chat.id, "<b>FEEDBACK FORM</b>")

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):

    data, chat_id = call.data, call.message.chat.id
    
    if data == "decline":
        bot.edit_message_caption("<b>🔴 VIDEO WAS NOT ADDED 🔴</b>",
            chat_id, call.message.id)

    elif data == "confirm":
        vdo_id = call.message.caption.split()[3]
        vdo_count = database.child("Users").child(chat_id).child("videos").get().val()
        if vdo_count == 0:
            database.child("Users").child(chat_id).child("videos").set(1)
            database.child("Users").child(chat_id).child("video_ids").set([vdo_id])
        else:
            vdo_set = set(database.child("Users").child(
                chat_id).child("video_ids").get().val() + [vdo_id])
            database.child("Users").child(chat_id).child("videos").set(len(vdo_set))
            database.child("Users").child(chat_id).child("video_ids").set(list(vdo_set))
        bot.edit_message_caption("<b>🟢 ADDED SUCCESSFULLY 🟢</b>",
            chat_id, call.message.id)        

    elif data == "add":
        bot.delete_message(chat_id, call.message.id)
        url = bot.send_message(chat_id,
            "<b>Send the URL of the YouTube video 👇🏻</b>")
        bot.register_next_step_handler(url, chk_vdo)    

    elif data == "del":
        bot.delete_message(chat_id, call.message.id)
        vdo_count = database.child("Users").child(chat_id).child("videos").get().val()
        if vdo_count == 0:
            bot.send_message(chat_id, "<b>NO VIDEOS FOUND! 🙃</b>")
        else:
            vdo_set = list(set(database.child("Users").child(chat_id).child(
                "video_ids").order_by_key().get().val()))
            bot.send_photo(chat_id, f"https://img.youtube.com/vi/{vdo_set[0]}/0.jpg",
            f"<b>STORED VIDEO ID ➜ <code>{vdo_set[0]}</code>\n\nDo you want to remove this?</b>",
            reply_markup=InlineKeyboardMarkup().add(*[
                InlineKeyboardButton("⬅️ BACK ", callback_data=f"back-1"),
                InlineKeyboardButton("DELETE 🔴", callback_data="delete"),
                InlineKeyboardButton("NEXT ➡️", callback_data=f"next-1"),]))
                
    elif data[:4] == "next":
        num = int(data.split("-")[1])
        vdo_set = list(set(database.child("Users").child(chat_id).child(
            "video_ids").order_by_key().get().val()))
        if num < len(vdo_set):
            try:
                bot.edit_message_media(InputMediaPhoto(f"https://img.youtube.com/vi/{vdo_set[num]}/0.jpg"),
                    chat_id, call.message.id)
            except:
                bot.edit_message_media(chat_id=chat_id, message_id=call.message.id,media=InputMediaPhoto(
                "AgACAgUAAxkBAAP4YggIzOFt-S8ILnVkwP8oILg6v_0AAtiwMRsOeUBUkdKMJfCjPf8BAAMCAAN5AAMjBA"))
            bot.edit_message_caption(f"<b>STORED VIDEO ID ➜ <code>{vdo_set[num]}</code>\n\
                \nDo you want to remove this?</b>", chat_id, call.message.id,
                reply_markup=InlineKeyboardMarkup().add(*[
                InlineKeyboardButton("⬅️ BACK ", callback_data=f"back-{num+1}"),
                InlineKeyboardButton("DELETE 🔴", callback_data="delete"),
                InlineKeyboardButton("NEXT ➡️", callback_data=f"next-{num+1}"),]))
        else:
            bot.answer_callback_query(call.id, "⚠️ END OF LIST ⚠️", show_alert=True)

    elif data[:4] == "back":
        num = int(data.split("-")[1])
        vdo_set = list(set(database.child("Users").child(chat_id).child(
            "video_ids").order_by_key().get().val()))
        if num - 1 in range(0, len(vdo_set) + 1):
            try:
                bot.edit_message_media(InputMediaPhoto(f"https://img.youtube.com/vi/{vdo_set[num-2]}/0.jpg"),
                    chat_id, call.message.id)
            except:
                bot.edit_message_media(chat_id=chat_id, message_id=call.message.id,media=InputMediaPhoto(
                "AgACAgUAAxkBAAP4YggIzOFt-S8ILnVkwP8oILg6v_0AAtiwMRsOeUBUkdKMJfCjPf8BAAMCAAN5AAMjBA"))
            bot.edit_message_caption(f"<b>STORED VIDEO ID ➜ <code>{vdo_set[num-2]}</code>\n\
                \nDo you want to remove this?</b>", chat_id, call.message.id,
                reply_markup=InlineKeyboardMarkup().add(*[
                InlineKeyboardButton("⬅️ BACK ", callback_data=f"back-{num-1}"),
                InlineKeyboardButton("DELETE 🔴", callback_data="delete"),
                InlineKeyboardButton("NEXT ➡️", callback_data=f"next-{num-1}"),]))
        else:
            bot.answer_callback_query(call.id, "⚠️ START OF LIST ⚠️", show_alert=True)

    elif data == "delete":
        id = call.message.caption.split()[4]
        vdo_set = database.child("Users").child(
            chat_id).child("video_ids").get().val()
        vdo_set.remove(id)
        
        database.child("Users").child(chat_id).child("video_ids").set(list(vdo_set))
        database.child("Users").child(chat_id).child("video").set(len(vdo_set))
        
        bot.edit_message_caption("<b>🔴 DELETED SUCCESSFULLY 🔴</b>",
            chat_id, call.message.id)
    
    elif data[:4] == "sch-":
        sch = int(data[-1])
        bot.delete_message(chat_id, call.message.id)
        database.child("Users").child(chat_id).child("sch").set(sch)
        bot.send_message(chat_id, f"<b>SCHEDULE CHANGED ✅</b>")

    elif data == "change":
        bot.delete_message(chat_id, call.message.id)
        schedule(call.message)

    elif data == "channel":
        bot.delete_message(chat_id, call.message.id)
        channel(call.message)

    elif data == "videos":
        bot.delete_message(chat_id, call.message.id)
        videos(call.message)  

    elif data == "analytics":
        bot.delete_message(chat_id, call.message.id)
        analytics(call.message)               

    elif data == "authorize":
        bot.delete_message(chat_id, call.message.id)
        bot.send_message(chat_id, "<b>To use this feature, kindly authenticaate below 👇🏼</b>",
        reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(text="AUTHENTICATE NOW ✅",
            url=f"http://youtube-bot.crazymarvin.com/authorize/{chat_id}")))
    
    elif data == "revoke":
        bot.delete_message(chat_id, call.message.id)
        database.child("OAuth2 Verified").child(chat_id).remove()
        database.child("Users").child(chat_id).child("channel_id").remove()
        database.child("Users").child(chat_id).child("title").remove()
        database.child("Users").child(chat_id).child("logo_url").remove()
        bot.send_message(chat_id, "<b>🔴 ACCESS REVOKED 🔴</b>")
                   
bot.infinity_polling()
