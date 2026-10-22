# Hoops 1v1

A small 2D local-multiplayer basketball game built with pygame. Two players
share the keyboard and fight for the ball on a full court with a hoop on each
side.

## Run it

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| Action              | Player 1 (blue) | Player 2 (red)  |
| ------------------- | --------------- | --------------- |
| Move                | `A` / `D`       | `←` / `→`       |
| Jump                | `W`             | `↑`             |
| Pump fake           | `S`             | `RShift`        |
| Shoot / steal       | `F`             | `↓`             |
| Restart / quit      | `R` / `Esc`     | `R` / `Esc`     |

- **Shoot:** hold the shoot key to charge, then release. The dotted arc shows
  where the ball will go, so release when the arc drops through the hoop.
- **Pump fake:** tap the pump fake key to raise the ball without shooting.
  You cannot start a shot until the fake finishes.
- **Steal:** tap shoot while standing next to the ball carrier.
- **Score:** each player attacks one hoop (blue attacks right, red attacks
  left). Baskets are worth 2 points, or 3 when the shot starts behind the
  dashed three-point line.
- **Inbound:** after a made basket, the ball drops through the net and the
  conceding player restarts with it under that hoop.
- **Game:** 90 seconds. The higher score wins; press `R` for a rematch.

## Project layout

| File            | Responsibility                                         |
| --------------- | ------------------------------------------------------ |
| `main.py`       | Window setup and entry point                           |
| `game.py`       | Loop, input wiring, possession, scoring, game states   |
| `player.py`     | Movement, jumping, charging, drawing                   |
| `ball.py`       | Ball physics, rim/backboard/floor collisions           |
| `hoop.py`       | Hoop geometry and score detection                      |
| `court.py`      | Court surface, markings and the two hoops              |
| `controls.py`   | Key maps and per-frame input states                    |
| `ui.py`         | Scoreboard, messages and end-of-game screen            |
| `constants.py`  | All tuning values (physics, rules, colours)            |
