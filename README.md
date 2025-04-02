# Multiplayer Tetris

Classic Tetris game for 1-4 players, featuring an AI client. Compete with up to 4 clients on the same network (you may add AI players). 

**Made by Aviv Friedman 2024 as part of a final project of the year at school.**

## Screenshots

### Start & End Images
<img src="https://github.com/JustSpring/multiplayer-tetris/assets/87150546/db2281b5-6bd3-4b59-bc1c-598e13a2351a" width=40%>
<img src="https://github.com/JustSpring/multiplayer-tetris/assets/87150546/258d1a20-16ea-4d02-ad9d-9f62825cc980" width=40%>

### Solo Mode
<img src="https://github.com/JustSpring/multiplayer-tetris/assets/87150546/dbc2c562-431f-43ad-aee9-b7e0511ce5b2" width=80%>

### Multiplayer Mode
<img src="https://github.com/JustSpring/multiplayer-tetris/assets/87150546/f3ad3d6c-c899-45a0-bee6-60b8839e02b3" width=70%>

## Features
- **Single-player mode**: Enjoy the classic Tetris experience on your own.
- **Multiplayer mode**: Compete with up to 4 players on the same network.
- **AI players**: Add AI players to the game to increase the challenge.
- **Network Play**: Play against friends or AI over a local network.
- **Hold Feature**: Hold pieces for later use to strategize your game.
- **Next Piece Preview**: See the next piece to plan your moves ahead.
- **Score Tracking**: Keep track of your score and aim for the high score.
- **Dynamic Speed Increase**: Game speed increases as you progress, making the game more challenging.
- **Ghost Piece**: Preview where the current piece will land to make precise moves.
- **Clear Lines and Send to Opponents**: Send lines to opponents when you clear lines, adding a competitive edge.
- **Game Over and Restart Options**: Easily restart the game or go back to the main menu after a game over.
- **High Score Database**: Track the best scores and see who holds the top spot.  

## Running the Game

To run this project, you will need to follow the next steps:

1. Download all provided files.
2. Start the server:
   ```
   python server.py
   ```
3. Run the game on each computer you want to play:
   ```
   python game.py
   ```
4. (Optional) Run the AI client:
   ```
   python ai_bot.py
   ```
5. Insert the server IP in the game clients (can be found using `ipconfig` in Command Prompt)

## AI Bot

I integrated an AI bot using the logic made by Yiyuan Lee. Full explanation can be found on [Yiyuan Lee's Tetris AI GitHub repository](https://github.com/LeeYiyuan/tetrisai).

### Basics of the AI:
The AI bot uses a combination of heuristics to decide the best possible moves for each tetromino. These heuristics include:
- **Aggregate Height**: The sum of the heights of all columns. Lower aggregate heights are preferred.
- **Complete Lines**: The number of complete lines that will be cleared with the current move. More lines are better.
- **Holes**: The number of empty spaces that have at least one block above them. Fewer holes are better.
- **Bumpiness**: The difference in heights between adjacent columns. Less bumpiness is better.

The AI evaluates possible moves based on these heuristics and selects the move with the best overall score.
![AI BOT](https://github.com/JustSpring/multiplayer-tetris/assets/87150546/d1683904-63cd-4b02-b514-c57874816ef0)

## Single-Player Cognitive Load Mode
The `single_player.py`  is uniquely designed to test cognitive load. In addition to offering the classic Tetris experience, this mode serves as a practical tool for evaluating how players manage and respond to increasing mental demands1.

## Controls

- **Left Arrow**: Move left
- **Right Arrow**: Move right
- **Up Arrow**: Rotate clockwise
- **Down Arrow**: Soft drop
- **Spacebar**: Hard drop
- **Shift**: Hold


## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License. 
