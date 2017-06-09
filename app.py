import os

from flask import Flask, render_template, request, redirect, url_for, jsonify
from opentok import OpenTok
from opentok import MediaModes


app = Flask(__name__)

try:
    apiKey = os.environ['API_KEY']
    secret = os.environ['API_SECRET']

except Exception:
    raise Exception('You must define API_KEY and API_SECRET environment variables')

if not apiKey or not secret:
  print('=========================================================================================================')
  print('')
  print('Missing TOKBOX_API_KEY or TOKBOX_SECRET')
  print('Find the appropriate values for these by logging into your TokBox Dashboard at: https://tokbox.com/account/#/')
  print('Then add them as an environment variables' )
  print('')
  print('=========================================================================================================')


opentok = OpenTok(apiKey, secret)

# IMPORTANT: roomToSessionIdDictionary is a variable that associates room names with unique
# unique sesssion IDs. However, since this is stored in memory, restarting your server will
# reset these values if you want to have a room-to-session association in your production
# application you should consider a more persistent storage

roomToSessionIdDictionary = {}

# returns the room name, given a session ID that was associated with it
def findRoomFromSessionId(sessionId):
  return roomToSessionIdDictionary[sessionId]


@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

@app.route('/session', methods=['GET'])
def session():
  return redirect(url_for('room', name="session"))

@app.route('/room/<name>', methods=['GET'])
def room(name='session'):
  roomName = name
  sessionId = []
  token = []
  print('attempting to create a session associated with the room: ' + roomName)

  # if the room name is associated with a session ID, fetch that
  try:
    sessionId = roomToSessionIdDictionary[roomName]

    # generate token
    token = opentok.generate_token(sessionId)
    return jsonify(apiKey=apiKey, sessionId=sessionId, token=token)

  # if this is the first time the room is being accessed, create a new session ID
  except KeyError:
    session = opentok.create_session(media_mode=MediaModes.routed)

    # now that the room name has a session associated with it, store it in memory
    # IMPORTANT: Because this is stored in memory, restarting your server will reset these values
    # if you want to store a room-to-session association in your production application
    # you should use a more persistent storage for them
    roomToSessionIdDictionary[roomName] = session.session_id;

    # generate token
    token = opentok.generate_token(session.session_id)
    return jsonify(apiKey=apiKey, sessionId=session.session_id, token=token)



@app.route('/archive/start', methods=['POST'])
def startArchive():
  json = request.body
  sessionId = json.sessionId
  archive = opentok.start_archive(sessionId, name=findRoomFromSessionId(sessionId))
  archive_id = archive.id

  return

if __name__ == '__main__':
  app.debug = True
  app.run()
