import os
import flask
import telebot
import pyrebase
import google_auth_oauthlib.flow
import google.oauth2.credentials
from googleapiclient.discovery import build
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="os.getenv("SENTRY_DSN")",
    integrations=[FlaskIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)


CLIENT_SECRETS_FILE = r"google-credentials.json" # https://devdojo.com/bryanborge/adding-google-cloud-credentials-to-heroku

SCOPES = [
  "https://www.googleapis.com/auth/youtube.readonly",
  "https://www.googleapis.com/auth/yt-analytics.readonly",
  "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
] 

TELEGRAM_API_KEY = os.getenv("API_KEY")

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

app = flask.Flask(__name__)
app.secret_key = b'flask-secret'    # https://flask.palletsprojects.com/quickstart/#sessions
bot = telebot.TeleBot(TELEGRAM_API_KEY, parse_mode="HTML")

firebase = pyrebase.initialize_app(config)
database = firebase.database()

@app.route('/')
def index():
    return flask.render_template("Home.html")


@app.route('/authorize/<user_id>')
def authorize(user_id):

    users = [user.key() for user in database.child("Users").get().each()]
    if str(user_id) not in users:
        return flask.redirect("https://t.me/YouTubeStatisticsBot")

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline', include_granted_scopes='true')

    flask.session['state'] = state
    flask.session['telegram_user_id'] = user_id

    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    state = flask.session['state']
    user_id = flask.session['telegram_user_id']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    youtube = get_service("youtube", "v3", credentials_to_dict(credentials))
    channel = execute_api_request(
        youtube.channels().list,
        mine=True,
        part='snippet',
    )
    
    try:    channel_id = channel["items"][0]["id"]
    except: channel_id = None

    try:    logo_url = channel["items"][0]["snippet"][
        "thumbnails"]["medium"]["url"]
    except: logo_url = None

    try:    title = channel["items"][0]["snippet"]["title"]
    except: title = None

    if channel_id == None: 
        bot.send_message(int(user_id), "<b>NO CHANNEL FOUND! 😕</b>")
    else:
        database.child("OAuth2 Verified").child(
            str(user_id)).set(flask.session['credentials'])
        database.child("Users").child(str(user_id)).child("channel_id").set(channel_id)
        database.child("Users").child(str(user_id)).child("logo_url").set(logo_url)
        database.child("Users").child(str(user_id)).child("title").set(title)
        bot.send_message(int(user_id), "<b>🟢 AUTHORIZATION SUCCESSFUL 🟢</b>")

    return flask.redirect("https://t.me/YouTubeStatisticsBot")


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True)
