# Game Rules

This document specifies the rules for the card game "Cheat" as implemented in this project's environment.

## 1. Objective

The primary objective is to be the first player to get rid of all cards from your hand.

## 2. First Round

The game begins with the first player, who must perform the following actions:
* Select 1 to 6 cards from their hand.
* Place the selected cards face-down onto the discard pile.
* Announce a rank for the cards played (e.g., "three Kings").

## 3. Subsequent Player Options

Following the first player, the turn proceeds sequentially. On their turn, a player has three options:

* **PLAY:** Play 1 to 6 cards from their hand face-down, claiming they are of the rank announced by the previous player.
* **PASS:** Forfeit the turn without playing any cards.
* **CHALLENGE:** Doubt the previous player's move.

## 4. Challenge Mechanic

When a challenge is initiated, the cards from the last play are revealed to all players.

* **`->` If the play was a LIE:**
    * The player who made the lie must pick up the entire discard pile.
    * The player who made the correct challenge starts the next round and can announce any rank.

* **`->` If the play was the TRUTH:**
    * The player who made the incorrect challenge must pick up the entire discard pile.
    * The player who was telling the truth starts the next round and can announce any rank.

## 5. Additional Rules

* **`Note 1: What Constitutes a Lie?`** A play is considered a lie if one or more of the played cards do not match the announced rank. Jokers are an exception (see below).

* **`Note 2: All Players Pass`** If all players in sequence pass their turn, the round ends. The last player to have successfully played cards starts the next round. The discard pile is cleared, and a new pile is started.

* **`Note 3: The "Honest Win" Rule`** A player can only win the game if their final move is truthful. If a player empties their hand on a lie, the win is voided, that player must pick up the entire discard pile, and the game continues.

## 6. The Joker

The Joker card is a wild card. It can be used to represent any rank and is always considered a "truthful" card during a challenge.