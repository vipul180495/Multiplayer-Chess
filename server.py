
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import chess
import chess_logic
import os

connected_users = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

game_board = chess.Board()

################################################################################
@socketio.on('join')
def handle_join(data):
    name = data.get('name', 'Anonymous')
    connected_users[request.sid] = name
    emit('users', list(connected_users.values()), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    connected_users.pop(request.sid, None)
    emit('users', list(connected_users.values()), broadcast=True)

@socketio.on('chat')
def handle_chat(data):
    emit('chat', {'name': data['name'], 'message': data['message']}, broadcast=True)
################################################################################

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('reset')
def handle_reset():
    global game_board
    game_board = chess.Board()
    emit('reset', broadcast=True)

@socketio.on('move')
def handle_move(data):
    move_uci = data['move']
    if chess_logic.is_valid_move(game_board, move_uci):
        game_board.push_uci(move_uci)
        emit('move', {'move': move_uci}, broadcast=True)
        if game_board.is_game_over():
            emit('game_over', {'result': game_board.result()}, broadcast=True)
    else:
        emit('invalid_move', {'move': move_uci})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
'''

from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
'''