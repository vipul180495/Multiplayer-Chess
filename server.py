
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import chess
import chess_logic
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

game_board = chess.Board()

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