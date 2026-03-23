# Card Game - DouDiZhu
(Since I am not particularly skilled at developing web-based games, you may need to install some dependencies to support running this locally before launching it -- Pygame)

Please take the time to read through the introduction below. Thank you.😀

Here are the specific steps:
1. Open my GitHub project page, click on "Code" -> "Download ZIP," and then unzip the downloaded file.
2. Open a terminal window (use PowerShell or CMD on Windows; use Terminal on macOS/Linux).
3. Type "cd" (followed by a space). Then, either drag the unzipped project folder directly into the terminal window and press Enter, or manually type out the folder's file path (e.g., windows:`cd "D:\xxx\pygame-doudizhu-main"`, macOS/Linux:`~/xxx/pygame-doudizhu-main`).
4. Windows Users:
Type "python -m pip install pygame-ce", and then type "python main.py" to launch the game.
5. macOS / Linux Users:
Type "python3 -m pip install pygame-ce", and then type "python3 main.py" to launch the game.


**If you are not yet familiar with how to play "Dou Dizhu", please read the game rules:**

Important!! Card rankings start from 3 and ascend in the following order: 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K, A, SJ (Small Joker), BJ (Big Joker). (Note: The Ace [A] functions as the number 1.)

Your objective is to play all of your cards before your opponents do. There are three players in total (you and two computer opponents), and each player is dealt 17 cards, the "Landlord" has 20.

The "Bidding for Landlord" Phase

Three cards are placed at the top of the screen; these are known as the "Landlord Cards." Before the game begins, the player holding the 3 of Hearts starts the bidding process. Moving clockwise, each player may choose to "Bid" (attempt to become the Landlord) or "Skip" (pass). The first player to successfully bid becomes the Landlord (indicated by a Landlord hat icon) and claims the three Landlord Cards. At this point, the game shifts to a 1-vs-2 format (the Landlord against the two "Peasants").

The Game

The Landlord plays first hand to start the game. The player currently holding the turn may play any valid card combination (all valid card combinations are listed at the bottom). Subsequent players must play in turn, matching the *same card combination type* as the previous player, but using a *higher-ranking* set of cards. Click on the cards you wish to play, then click the "Play" button; if you have no valid cards to play, click "Skip." The game ends when one player has played all their cards; click "Restart" in the center of the screen to begin a new game.
s

**All Card Combinations:**

Single Card(单张)  — One individual card (e.g., 3)

Pair(对子)  — Two identical cards (e.g., 44)

Triples(三张)  — Three identical cards (e.g., 555)

Triples with a Single(三带一)  — Three identical cards accompanied by one arbitrary single card (e.g., 666 7)

Triples with a Pair(三带二)  — Three identical cards accompanied by one arbitrary pair (e.g., 888 99)

Straight(顺子)  — Five or more consecutive single cards; cannot extend beyond the 2 (e.g., 3 4 5 6 7 8 9 10 J Q K A; the Ace is the highest card allowed)

Consecutive Pairs(连对)  — Three or more consecutive pairs; cannot extend beyond the 2 (e.g., 33 44 55)

Consecutive Triples(三顺、飞机)  — Two sets of consecutive triples; cannot extend beyond the 2 (e.g., KKK AAA)

Airplane with Wings (Singles)(飞机带翅膀)  — Consecutive triples accompanied by two arbitrary single cards (e.g., 333 444 5 6)

Airplane with Wings (Pairs)(飞机带两对)  — Consecutive triples accompanied by two arbitrary pairs (e.g., 555 666 77 88)

Bomb(炸弹)  — Four identical cards; can be played after any other card combination and possesses immense power (e.g., 3333)

Four-of-a-Kind with Two Singles(四带二单)  — A Bomb accompanied by two arbitrary single cards; loses the explosive power of a standalone Bomb (e.g., 4444 5 6)

Four-of-a-Kind with Two Pairs(四带二对)  — A Bomb accompanied by two arbitrary pairs; loses the explosive power of a standalone Bomb (e.g., 5555 66 77)

Rocket (Jokers)(王炸)  — The Big Joker and the Little Joker; can beat any other card combination and is more powerful than a standard Bomb (e.g., SJ BJ; Tip: Save this for a critical moment!)


If you encounter any issues, please contact me (or try asking ChatGPT). 
**murphy.paperking@gmail.com**
