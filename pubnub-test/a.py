import keys
from pubnub import Pubnub

pubnub = Pubnub(publish_key=keys.PUB_KEY, subscribe_key=keys.SUB_KEY)

def callback(message):
  print(message)

pubnub.publish('my_channel_sf23', 'Hello from PubNub Python SDK!', callback=callback, error=callback)


while True:
  pubnub.publish('my_channel_sf23', raw_input(), callback=callback, error=callback)

