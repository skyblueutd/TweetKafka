from kafka import SimpleProducer, KafkaClient
import tweepy

topic = 'twitterstream'
class TweeterStreamListener(tweepy.StreamListener):
    """ A class to read the twitter stream and push it to Kafka"""

    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        kafkaclient = KafkaClient("localhost:9092")
        self.producer = SimpleProducer(kafkaclient, async = True,
                          batch_send_every_n = 1000,
                          batch_send_every_t = 10)

    def on_status(self, status):
        """ This method is called whenever new data arrives from live stream.
        We asynchronously push this data to kafka queue"""
        message =  status.text.encode('utf-8')
        try:
            self.producer.send_messages(topic, message)
        except Exception as e:
            print(e)
            return False
        return True

    def on_timeout(self):
        return True # Don't kill the stream

    def on_error(self, status_code):

        print('Got an error with status code: ' + str(status_code))
        return True  # To continue listening

if __name__ == '__main__':

    # tweet connections
    access_token = "your twitter account info here"
    access_token_secret = "your twitter account info here"
    consumer_key = "your twitter account info here"
    consumer_secret = "your twitter account info here"

    # Create Auth object
    authority = tweepy.OAuthHandler(consumer_key, consumer_secret)
    authority.set_access_token(access_token, access_token_secret)
    api = tweepy.API(authority)

    # Create stream and bind the listener to it
    streaming = tweepy.Stream(authority, listener = TweeterStreamListener(api))

    streaming.filter(track=['trump', 'obama'], languages = ['en'])
