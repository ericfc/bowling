from django.db import models


class Game(models.Model):
    is_ongoing = models.BooleanField(default=True)


class Player(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name='players'
    )
    name = models.CharField(max_length=255)


class Frame(models.Model):
    STRIKE = 'STRIKE'
    SPARE = 'SPARE'
    OPEN = 'OPEN'
    ROLLING = 'ROLLING'
    FRAME_TYPE_CHOICES = (
        (STRIKE, STRIKE),
        (SPARE, SPARE),
        (OPEN, OPEN),
        (ROLLING, ROLLING)
    )
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='frames'
    )
    frame_number = models.PositiveIntegerField()
    frame_type = models.CharField(
        max_length=7, choices=FRAME_TYPE_CHOICES, default=ROLLING
    )


class Roll(models.Model):
    frame = models.ForeignKey(
        Frame, on_delete=models.CASCADE, related_name='rolls'
    )
    pins_knocked_down = models.IntegerField()
    roll_number = models.IntegerField()
