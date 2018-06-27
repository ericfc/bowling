# Bowling Score Rest API
This is a REST API implemented in Django. It provides endpoints to create a bowling game with any number of players, retrieve the status of the game, and update the game by creating rolls.

## Running application with Docker
After installing Docker you may run
`docker-compose up`
from the base directory.
It will build the necessary image and start a container.
The app will be running on `localhost:8000`

At this point you may run unit tests:
`docker-compose exec web python manage.py test`


## API
To begin a new game create a `POST` request to
`/games/`
providing a list of player names
```
{
    "player_names": ["alice", "bob"]
}
```

Player score boards will be created consisting of ten empty frames.
The reponse will be the full bowling game board and the current status/score
```
{
    "id": 1,
    "is_ongoing": true,
    "players": [
        {
            "id": 1,
            "name": "alice",
            "frames": [
                {
                    "id": 1,
                    "frame_number": 1,
                    "rolls": [],
                    "frame_type": "ROLLING"
                },
                {
                    "id": 2,
                    "frame_number": 2,
                    "rolls": [],
                    "frame_type": "ROLLING"
                },
                {
                    "id": 3,
                    "frame_number": 3,
                    "rolls": [],
                    "frame_type": "ROLLING"
                },
                ...
                {
                    "id": 10,
                    "frame_number": 10,
                    "rolls": [],
                    "frame_type": "ROLLING"
                }
            ],
            "score": 0
        },
        ...
    ]
}
```

The status of all games may be retreived by submitting a `GET` request to
`/games/`

The status of any particular game may be retrieved by submitting a `GET` request to
`/games/<GAME_ID>/`

A player may attempt a roll by submitting a `POST` request to
`/games/<GAME_ID>/roll/`
and providing data on the roll
```
{
    "player_id": 1,
    "pins_knocked_down": 10
}
```
The roll will be recorded for the player and may be immediately retrieved.
It will continue to accept new rolls for a player until the player has exhausted all of their rolls.
Any future attempts to make rolls will result in `400` response:
```
{
    "detail": "bob has exhausted all their rolls"
}
```
