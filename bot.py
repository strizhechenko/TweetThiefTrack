# coding: utf-8

"""
Бот, который ищет оригинальные твиты популярных аккаунтов
"""

import sys
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from twitterbot_utils import Twibot

__author__ = "@strizhechenko"

SCHED = BlockingScheduler()
BOT = Twibot()
TIMEOUT = int(os.environ.get('timeout', 1000))
STEALER = os.environ.get('STEALER', 'leprasorium')
TWEETLINK = "https://twitter.com/%s/status/%s"

@SCHED.scheduled_job('interval', minutes=TIMEOUT)
def do_tweets():
    """ периодические генерация и постинг твитов """
    tweets = BOT.api.user_timeline(screen_name=STEALER, count=10)
    for tweet in tweets:
        real_tweets = BOT.api.search(tweet.text, max_id=tweet.id - 1)
        ids = [t.id for t in real_tweets
               if not t.text.startswith('RT') and not t.text.find('http') >= 0]
        if not ids:
            continue
        orig_id = min(ids)
        real_tweet = BOT.api.get_status(id=orig_id)
# pylint: disable=e1101
        user = real_tweet.user
# pylint: enable=e1101
        username = user.screen_name
        print tweet.text.encode('utf-8')
        template = u"Вероятно @%s спиздил свой твит %s отсюда %s" % (
            STEALER, TWEETLINK, TWEETLINK)
        bot_tweet = (template % (STEALER, tweet.id_str, username, str(orig_id)))
        print bot_tweet.encode('utf-8')
        BOT.tweet(bot_tweet, check_length=False)

if __name__ == '__main__':
    if '--wipe' in sys.argv:
        BOT.wipe()
        exit(0)
    do_tweets()
    if os.uname()[0] == 'Darwin' or '--test' in sys.argv:
        exit(0)
    else:
        SCHED.start()
