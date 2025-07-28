
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import chess
import chess_logic
import os

connected_users = {}
player_colors = {}  # socket_id -> 'white' or 'black'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

game_board = chess.Board()

################################################################################
'''@socketio.on('join')
def handle_join(data):
    name = data.get('name', 'Anonymous')
    connected_users[request.sid] = name
    emit('users', list(connected_users.values()), broadcast=True)'''
    
@socketio.on('join')
def handle_join(data):
    name = data.get('name', 'Anonymous')
    connected_users[request.sid] = name
    
    '''# Assign colors if not assigned
    if len(player_colors) < 2:
        if 'white' not in player_colors.values():
            player_colors[request.sid] = 'white'
        else:
            player_colors[request.sid] = 'black'
    else:
        player_colors[request.sid] = 'spectator'  # For extra users
            '''
     # Assign player color
    assigned_color = 'spectator'
    existing_colors = set(player_colors.values())

    if 'white' not in existing_colors:
        assigned_color = 'white'
    elif 'black' not in existing_colors:
        assigned_color = 'black'

    player_colors[request.sid] = assigned_color
    # Emit user list with colors
    users_info = [{'name': connected_users[sid], 'color': player_colors.get(sid, 'spectator')} for sid in connected_users]
    emit('users', users_info, broadcast=True)
    
    # Send current turn info
    emit('turn', {'turn': 'white' if game_board.turn else 'black'}, broadcast=True)
    
'''@socketio.on('disconnect')
def handle_disconnect():
    connected_users.pop(request.sid, None)
    emit('users', list(connected_users.values()), broadcast=True)'''
    
@socketio.on('disconnect')
def handle_disconnect():
    connected_users.pop(request.sid, None)
    player_colors.pop(request.sid, None)
    users_info = [{'name': connected_users[sid], 'color': player_colors.get(sid, 'spectator')} for sid in connected_users]
    emit('users', users_info, broadcast=True)
    

@socketio.on('chat')
def handle_chat(data):
    emit('chat', {'name': data['name'], 'message': data['message']}, broadcast=True)
    
@socketio.on('undo')
def handle_undo():
    player_color = player_colors.get(request.sid)
    
    # Only allow undo if opponent's turn (i.e., this player made last move)
    if player_color == 'white' and not game_board.turn:
        pass
    elif player_color == 'black' and game_board.turn:
        pass
    else:
        emit('undo_denied')
        return

    if len(game_board.move_stack) >= 1:
        game_board.pop()
        emit('undo', {'fen': game_board.fen()}, broadcast=True)
        emit('turn', {'turn': 'white' if game_board.turn else 'black'}, broadcast=True)
    
################################################################################

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('reset')
def handle_reset():
    global game_board
    game_board = chess.Board()
    emit('reset', broadcast=True)

'''@socketio.on('move')
def handle_move(data):
    move_uci = data['move']
    if chess_logic.is_valid_move(game_board, move_uci):
        game_board.push_uci(move_uci)
        emit('move', {'move': move_uci}, broadcast=True)
        if game_board.is_game_over():
            emit('game_over', {'result': game_board.result()}, broadcast=True)
    else:
        emit('invalid_move', {'move': move_uci})'''
        
@socketio.on('move')
def handle_move(data):
    move_uci = data['move']
    player_color = player_colors.get(request.sid)
    
    # Validate player is allowed to move
    if player_color != ('white' if game_board.turn else 'black'):
        emit('invalid_move', {'move': move_uci})
        return
    
    if chess_logic.is_valid_move(game_board, move_uci):
        game_board.push_uci(move_uci)
        emit('move', {'move': move_uci}, broadcast=True)
        # Emit turn info after move
        emit('turn', {'turn': 'white' if game_board.turn else 'black'}, broadcast=True)
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