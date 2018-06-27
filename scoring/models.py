from django.db import models


class Game(models.Model):
    is_ongoing = models.BooleanField(default=True)

    def update_is_ongoing(self):
        is_ongoing = Frame.objects.filter(
            player__game=self, frame_type=Frame.ROLLING
        ).exists()

        if not is_ongoing:
            self.is_ongoing = False
            self.save()


class Player(models.Model):
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name='players'
    )
    name = models.CharField(max_length=255)

    def make_roll(self, pins_knocked_down):
        """
        Create a new Roll on this Player if a valid Frame exists
        Return None otherwise
        """
        frame = self.frames.filter(
            frame_type=Frame.ROLLING
        ).order_by('frame_number').first()

        if frame is None:
            return None

        return frame.make_roll(pins_knocked_down)


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

    def _calculate_open_score(self):
        """
        Calculate the score on an OPEN Frame
        """
        return sum([roll.pins_knocked_down for roll in self.rolls.all()])

    def _calculate_spare_score(self):
        """
        Calculate the score on a SPARE Frame by finding the next Roll
        If there is no next roll return None
        """
        next_frame = Frame.objects.get(
            player=self.player,
            frame_number=self.frame_number + 1
        )

        third_roll = next_frame.rolls.order_by('roll_number').first()

        if third_roll is not None:
            return 10 + third_roll.pins_knocked_down

        return None

    def _calculate_strike_score(self):
        """
        Calculate the score on a STRIKE Frame by finding the next two Rolls
        If there are no next two rolls return None
        """
        next_frame_1 = Frame.objects.get(
            player=self.player,
            frame_number=self.frame_number + 1
        )

        if next_frame_1.frame_type == Frame.ROLLING:
            return None

        elif next_frame_1.frame_type in (Frame.OPEN, Frame.SPARE):
            return 10 + sum(
                [
                    roll.pins_knocked_down
                    for roll in next_frame_1.rolls.order_by(
                        'roll_number'
                    )[:2]
                ]
            )

        elif next_frame_1.frame_type == Frame.STRIKE:
            next_frame_2 = Frame.objects.get(
                player=self.player,
                frame_number=next_frame_1.frame_number + 1
            )

            third_roll = next_frame_2.rolls.order_by('roll_number').first()

            if third_roll is not None:
                return 20 + third_roll.pins_knocked_down

            return None

    def get_score(self):
        """
        Get the Frame score
        Return None if Rolls are pending
        """
        if self.frame_type == Frame.ROLLING:
            return None

        elif self.frame_type == Frame.OPEN:
            return self._calculate_open_score()

        elif self.frame_type == Frame.STRIKE:
            return self._calculate_strike_score()

        elif self.frame_type == Frame.SPARE:
            return self._calculate_spare_score()

    def make_roll(self, pins_knocked_down):
        """
        Make a new Roll on the Frame and return it
        Update the frame_type of the Frame
        Return None if Frame is complete
        """
        last_roll = self.rolls.order_by('roll_number').last()

        if last_roll is None:
            if pins_knocked_down == 10:
                if self.frame_number < 10:
                    self.frame_type = Frame.STRIKE

        elif last_roll.roll_number == 1:
            frame_total = last_roll.pins_knocked_down + pins_knocked_down

            if frame_total == 10:
                if self.frame_number < 10:
                    self.frame_type = Frame.SPARE

            elif frame_total < 10:
                self.frame_type = Frame.OPEN

        elif last_roll.roll_number == 2:
            if (
                self.frame_number < 10 or
                (self.frame_number == 10 and self.frame_type != Frame.ROLLING)
            ):
                return None

            elif self.frame_number == 10:
                self.frame_type = Frame.OPEN

        self.save()
        return Roll.objects.create(
            frame=self,
            pins_knocked_down=pins_knocked_down,
            roll_number=(
                last_roll.roll_number + 1 if last_roll is not None else 1
            )
        )


class Roll(models.Model):
    frame = models.ForeignKey(
        Frame, on_delete=models.CASCADE, related_name='rolls'
    )
    pins_knocked_down = models.IntegerField()
    roll_number = models.IntegerField()
