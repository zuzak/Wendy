from twisted.internet import defer
from ..transport import Event
from ..command import CommandPluginSuperclass
from .. import constants
import re
import tweepy
import datetime


def relative_date(d):
    diff = datetime.datetime.utcnow() - d
    s = diff.seconds
    if diff.days > 7 or diff.days < 0:
        return d.strftime('%d %b %y')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{} minutes ago'.format(s / 60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{} hours ago'.format(s / 3600)


class Twitter(CommandPluginSuperclass):
    REQUIRES = ["ircop.OpProvider", "ircutil.Names"]
    DEFAULT_CONFIG = {
        "OAUTH_CONSUMER_KEY": "",  # Twitter oauth info. Get deets from https://apps.twitter.com/
        "OAUTH_CONSUMER_SECRET": "",
        "OAUTH_ACCESS_TOKEN": "",
        "OAUTH_ACCESS_SECRET": "",
        "channels": None,  # Channels in which the bot should make do stuff
        "expand_urls": True,  # Whether or not to expand URLs in tweets
        "strip_media_links": True,  # Whether or not to strip out links to media (e.g. images) associated with tweet
        "strip_newlines": True  # Strip out newlines from tweets, because they make newlines in IRC.
    }

    TWITTER_URL_REGEX = "https?://twitter\.com/(.+?)/status/([0-9]+)/?"

    twitter_api = None

    def __init__(self, *args, **kwargs):
        super(Twitter, self).__init__(*args, **kwargs)

        auth = tweepy.OAuthHandler(self.config['OAUTH_CONSUMER_KEY'], self.config['OAUTH_CONSUMER_SECRET'])
        auth.set_access_token(self.config['OAUTH_ACCESS_TOKEN'], self.config['OAUTH_ACCESS_SECRET'])

        self.twitter_api = tweepy.API(auth)

    @defer.inlineCallbacks
    def on_event_irc_on_privmsg(self, event):
        super(Twitter, self).on_event_irc_on_privmsg(event)

        # Don't do anything unless the channel the message originates from is in our config
        if event.channel not in self.config["channels"]:
            return

        nick = event.user.split("!")[0]
        twitter_regex_matches = re.findall(self.TWITTER_URL_REGEX, event.message)

        # Turn regex groups into vararables that I can be an progreammer with.
        for twat, tweet_id in twitter_regex_matches:

            # Get tweet dater
            try:
                tweet = self.twitter_api.get_status(tweet_id)
            except tweepy.TweepError:
                # There was an error so let's not do a FOCKEN THING.
                return

            tweet_msg = tweet.text

            # Expand links in tweet
            if self.config['expand_urls']:
                for url in tweet.entities.get('urls', []):
                    tweet_msg = tweet_msg.replace(url.get('url'), url.get('expanded_url'))

            # Filter out media links
            if self.config['strip_media_links']:
                for media in tweet.entities.get('media', []):
                    tweet_msg = tweet_msg.replace(media.get('url'), '')

            # Filter out newlines
            if self.config['strip_newlines']:
                tweet_msg = tweet_msg.replace('\n', ' ')

            # Construct the message to send to IRC
            irc_message = "{BOLD}{COLOUR}{NAVY_BLUE}{tweet_author}{NORMAL} tweeted {COLOUR}{GREEN}{tweet_date}{NORMAL}: {COLOUR}{DARK_GRAY}{tweet_msg}".format(
                tweet_author=tweet.author.screen_name,
                tweet_date=relative_date(tweet.created_at),
                tweet_msg=tweet_msg,
                BOLD=constants.BOLD,
                NAVY_BLUE=constants.NAVY_BLUE,
                GREEN=constants.GREEN,
                DARK_GRAY=constants.DARK_GRAY,
                COLOUR=constants.COLOR_TAG,
                NORMAL=constants.NORMAL
            )

            # Oh we have a twitters con fuckin grats.
            self.transport.send_event(
                Event("irc.do_msg", user=event.channel, message=irc_message)
            )