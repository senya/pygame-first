import keys
from pubnub import Pubnub

pubnub = Pubnub(publish_key=keys.PUB_KEY, subscribe_key=keys.SUB_KEY)

def _callback(message, channel):
  print(message)

def _error(message):
  print(message)

pubnub.subscribe(channels="my_channel_sf23", callback=_callback, error=_error)

while True:
  pass
