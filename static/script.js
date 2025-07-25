console.log("✅ script.js loaded");

const socket = io();
const game = new Chess();
const whiteCaptures = [];
const blackCaptures = [];

const board = Chessboard('board', {
  draggable: true,
  position: 'start',
  pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png',
  onDrop: onDrop
});

function onDrop(source, target) {
  const move = game.move({
    from: source,
    to: target,
    promotion: 'q'
  });

  if (move === null) return 'snapback';

  // Capture handling
  if (move.captured) {
    const capturedSymbol = move.captured;
    const takenPiece = move.color === 'w' ? 'b' + capturedSymbol.toUpperCase() : 'w' + capturedSymbol.toUpperCase();
    addCapturedPiece(move.color, takenPiece);
  }

  board.position(game.fen());
  socket.emit('move', { move: move.from + move.to });
}

socket.emit('reset');

socket.on('reset', () => {
  game.reset();
  board.start();
  document.getElementById('white-captures').innerHTML = '';
  document.getElementById('black-captures').innerHTML = '';
  document.getElementById('status').innerText = '';
});

//////////////////////////// Added code///////////////////////////////
let playerName = prompt("Enter your name") || "Anonymous";
socket.emit("join", { name: playerName });

socket.on("users", (users) => {
  const userList = document.getElementById("user-list");
  userList.innerHTML = "";
  users.forEach((name) => {
    const li = document.createElement("li");
    li.innerText = name;
    userList.appendChild(li);
  });
});

document.getElementById("send-chat").onclick = () => {
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (message !== "") {
    socket.emit("chat", { name: playerName, message });
    input.value = "";
  }
};

socket.on("chat", (data) => {
  const log = document.getElementById("chat-log");
  const entry = document.createElement("div");
  entry.innerHTML = `<strong>${data.name}:</strong> ${data.message}`;
  log.appendChild(entry);
  log.scrollTop = log.scrollHeight;
});
/////////////////////////////////////////////////////////////////////////

socket.on('move', data => {
  const moveUCI = data.move;

  const lastMove = game.history({ verbose: true }).slice(-1)[0];
  const lastUCI = lastMove ? lastMove.from + lastMove.to : '';
  if (lastUCI === moveUCI) return;

  const move = game.move({
    from: moveUCI.slice(0, 2),
    to: moveUCI.slice(2, 4),
    promotion: 'q'
  });

  if (move) {
    if (move.captured) {
      const capturedSymbol = move.captured;
      const takenPiece = move.color === 'w' ? 'b' + capturedSymbol.toUpperCase() : 'w' + capturedSymbol.toUpperCase();
      addCapturedPiece(move.color, takenPiece);
    }

    board.position(game.fen());
  }
});

socket.on('invalid_move', data => {
  alert("❌ Invalid move: " + data.move);
  game.undo();
  board.position(game.fen());
});

socket.on('game_over', data => {
  document.getElementById('status').innerText = "♟️ Game Over! Result: " + data.result;
});

// Add captured piece to UI
function addCapturedPiece(moverColor, pieceCodeRaw) {
  const pieceCode = pieceCodeRaw.charAt(0) + pieceCodeRaw.charAt(1).toUpperCase();  
  const imgSrc = `https://chessboardjs.com/img/chesspieces/wikipedia/${pieceCode}.png`;
  const img = document.createElement('img');
  img.src = imgSrc;
  img.style.height = '30px';
  img.style.marginRight = '5px';

  if (moverColor === 'w') {
    // white moved → captured black
    document.getElementById('white-captures').appendChild(img);
  } else {
    // black moved → captured white
    document.getElementById('black-captures').appendChild(img);
  }
}
