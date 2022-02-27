[![Telegram YouTube Statistics Bot](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://t.me/YouTubeStatisticsTelegramBot)
[![GitHub Actions](https://github.com/Crazy-Marvin/YouTubeStatsTelegramBot/actions/workflows/ci.yml/badge.svg)](https://github.com/Crazy-Marvin/YouTubeStatsTelegramBot/actions/workflows/ci.yml)
![healthchecks.io](https://img.shields.io/endpoint?url=https://healthchecks.io/badge/396c7d03-faf7-4562-9f83-1194d0/mtzkGiJc-2/YouTubeStats.shields)
[![License](https://img.shields.io/github/license/Crazy-Marvin/YouTubeStatsTelegramBot)](https://github.com/Crazy-Marvin/YouTubeStatsTelegramBot/blob/trunk/LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/Crazy-Marvin/YouTubeStatsTelegramBot.svg?style=flat)](https://github.com/Crazy-Marvin/YouTubeStatsTelegramBot/commits)
[![Releases](https://img.shields.io/github/downloads/Crazy-Marvin/YouTubeStatsTelegramBot/total.svg?style=flat)](https://github.com/Crazy-Marvin/YouTubeStatsTelegramBot/releases)
[![Latest tag](https://img.shields.io/github/tag/Crazy-Marvin/YouTubeStatsTelegramBot.svg?style=flat)](https://github.com/Crazy-Marvin/YouTubeStatsTelegramBot/tags)
[![Issues](https://img.shields.io/github/issues/Crazy-Marvin/YouTubeStatsTelegramBot.svg?style=flat)](https://github.com/Crazy-Marvin/YouTubeStatsTelegramBot/issues)
[![Pull requests](https://img.shields.io/github/issues-pr/Crazy-Marvin/YouTubeStatsTelegramBot.svg?style=flat)](https://github.com/Crazy-Marvin/YouTubeStatsTelegramBot/pulls)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a9ec4ee98a93425ca8162b369adce3db)](https://www.codacy.com/gh/Crazy-Marvin/YouTubeStatsTelegramBot/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Crazy-Marvin/YouTubeStatsTelegramBot&amp;utm_campaign=Badge_Grade)
[![Dependabot](https://badgen.net/badge/icon/dependabot?icon=dependabot&label)](https://python.org/)
![Snyk Vulnerabilities for GitHub Repo](https://img.shields.io/snyk/vulnerabilities/github/Crazy-Marvin/YouTubeStatsTelegramBot)
[![Telegram YouTube Statistics Bot](https://img.shields.io/badge/Python-yellow?logo=python)](https://t.me/YouTubeStatsTelegramBot)

# YouTube Statistics Telegram Bot

This [bot](http://t.me/YouTubeStatisticsBot) sends you update of YouTube videos. 

#### Commands

start - This starts the bot 🚀  
stats - This sends an overview of all tracked URLs + up- and downvotes and number of comments 🗣  
channel - This lets you see your channel statistics 🎥  
videos - This lets you see your videos' statistics 📼  
schedule - This lets you choose a schedule for automatic updates 🕰  
language - This lets you change the language 🌎  
help - This sends you a help text 🆘  
contact - This allows contact ✍️  
feedback - This lets you give feedback 👺  

### Requirements

- Token from [@Botfather](https://telegram.me/botfather)
- SSL certificate (I recommend [Let's Encrypt](https://letsencrypt.org/))
- Webserver running [Python](https://www.python.org) (tested with [Apache](https://httpd.apache.org/) & [NGINX](https://www.nginx.com/) but others should work too)
- API key from YouTube
- Google Cloud service account credentials (JSON) for accessing Google Sheets API, Google Drive API & [Firebase](https://firebase.google.com/) API
- [Sentry](https://docs.sentry.io/platforms/python/) key (optional)
- [Healthchecks](https://healthchecks.io/#php) URL (optional)

### Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Please make sure to update tests as appropriate.
More details may be found in the [CONTRIUBTING.md](https://github.com/Crazy-Marvin/YouTubeStatsTelegramBot/tree/trunk/.github/CONTRIBUTING.md).

### License

[MIT](https://choosealicense.com/licenses/mit/)
