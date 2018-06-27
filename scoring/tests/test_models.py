from django.test import TestCase
from unittest.mock import patch

from scoring.models import Frame, Game, Player, Roll


class GameTestCase(TestCase):
    def setUp(self):
        self.game = Game.objects.create()
        self.player = Player.objects.create(game=self.game)
        self.frame = Frame.objects.create(player=self.player, frame_number=1)

    def test_update_is_ongoing(self):
        """
        Test update_is_ongoing method
        """
        self.game.update_is_ongoing()
        self.assertTrue(self.game.is_ongoing)

        self.frame.frame_type = Frame.STRIKE
        self.frame.save()

        self.game.update_is_ongoing()
        self.assertFalse(self.game.is_ongoing)


class PlayerTestCase(TestCase):
    def setUp(self):
        self.game = Game.objects.create()
        self.player = Player.objects.create(game=self.game)
        self.frame = Frame.objects.create(player=self.player, frame_number=1)

    @patch.object(Frame, 'make_roll')
    def test_make_roll(self, mock_make_roll):
        """
        Test make_roll method
        """
        self.player.make_roll(10)
        mock_make_roll.assert_called_once_with(10)

        mock_make_roll.reset_mock()
        self.frame.frame_type = Frame.STRIKE
        self.frame.save()

        roll = self.player.make_roll(10)
        self.assertIsNone(roll)
        self.assertFalse(mock_make_roll.called)


class FrameTestCase(TestCase):
    def setUp(self):
        self.game = Game.objects.create()
        self.player = Player.objects.create(game=self.game)
        self.frame = Frame.objects.create(player=self.player, frame_number=1)
        self.frame2 = Frame.objects.create(player=self.player, frame_number=2)

    def test__calculate_open_score(self):
        """
        Test the calculation of OPEN Frame score
        """
        Roll.objects.bulk_create(
            [
                Roll(frame=self.frame, pins_knocked_down=1, roll_number=1),
                Roll(frame=self.frame, pins_knocked_down=6, roll_number=2)
            ]
        )
        score = self.frame._calculate_open_score()

        self.assertEqual(score, 7)

    def test__calculate_spare_score_pending(self):
        """
        Test the calculation of pending SPARE Frame score
        """
        score = self.frame._calculate_spare_score()
        self.assertIsNone(score)

    def test__calculate_spare_score(self):
        """
        Test the calculation of a valid SPARE Frame score
        """
        Roll.objects.create(
            frame=self.frame2, pins_knocked_down=3, roll_number=1
        )
        score = self.frame._calculate_spare_score()

        self.assertEqual(score, 13)

    def test__calculate_strike_score_pending(self):
        """
        Test the calculation of a pending STRIKE Frame score
        """
        score = self.frame._calculate_strike_score()
        self.assertIsNone(score)

        frame3 = Frame.objects.create(player=self.player, frame_number=3)
        self.frame2.frame_type = Frame.STRIKE
        self.frame2.save()

        score = self.frame._calculate_strike_score()
        self.assertIsNone(score)

    def test__calculate_strike_score(self):
        Roll.objects.bulk_create(
            [
                Roll(frame=self.frame2, pins_knocked_down=1, roll_number=1),
                Roll(frame=self.frame2, pins_knocked_down=6, roll_number=2)
            ]
        )
        self.frame2.frame_type = Frame.OPEN
        self.frame2.save()

        score = self.frame._calculate_strike_score()
        self.assertEqual(score, 17)

    @patch.object(Frame, '_calculate_open_score')
    @patch.object(Frame, '_calculate_spare_score')
    @patch.object(Frame, '_calculate_strike_score')
    def test_get_score(
        self,
        mock__calculate_strike_score,
        mock__calculate_spare_score,
        mock__calculate_open_score
    ):
        """
        Test getting of score for all Frame types
        """
        score = self.frame.get_score()
        self.assertIsNone(score)

        self.frame.frame_type = Frame.OPEN
        score = self.frame.get_score()
        self.assertEqual(score, mock__calculate_open_score.return_value)

        self.frame.frame_type = Frame.SPARE
        score = self.frame.get_score()
        self.assertEqual(score, mock__calculate_spare_score.return_value)

        self.frame.frame_type = Frame.STRIKE
        score = self.frame.get_score()
        self.assertEqual(score, mock__calculate_strike_score.return_value)

    def test_make_roll_first(self):
        """
        Test making a roll with no previous rolls
        """
        roll = self.frame.make_roll(3)
        self.assertEqual(self.frame.frame_type, Frame.ROLLING)
        self.assertEqual(roll.frame, self.frame)
        self.assertEqual(roll.pins_knocked_down, 3)
        self.assertEqual(roll.roll_number, 1)

        roll = self.frame2.make_roll(10)
        self.assertEqual(self.frame2.frame_type, Frame.STRIKE)
        self.assertEqual(roll.frame, self.frame2)
        self.assertEqual(roll.pins_knocked_down, 10)
        self.assertEqual(roll.roll_number, 1)

    def test_make_roll_second(self):
        """
        Test making a second Roll
        """
        self.frame.make_roll(3)
        roll = self.frame.make_roll(3)
        self.assertEqual(self.frame.frame_type, Frame.OPEN)
        self.assertEqual(roll.frame, self.frame)
        self.assertEqual(roll.pins_knocked_down, 3)
        self.assertEqual(roll.roll_number, 2)

        self.frame2.make_roll(1)
        roll = self.frame2.make_roll(9)
        self.assertEqual(self.frame2.frame_type, Frame.SPARE)
        self.assertEqual(roll.frame, self.frame2)
        self.assertEqual(roll.pins_knocked_down, 9)
        self.assertEqual(roll.roll_number, 2)

    def test_make_roll_third(self):
        """
        Test making a third Roll
        """
        self.frame.make_roll(1)
        self.frame.make_roll(2)
        roll = self.frame.make_roll(3)
        self.assertIsNone(roll)

        self.frame2.frame_number = 10
        self.frame2.save()
        self.frame2.make_roll(3)
        self.frame2.make_roll(7)
        roll = self.frame2.make_roll(10)
        self.assertEqual(self.frame2.frame_type, Frame.OPEN)
        self.assertEqual(roll.frame, self.frame2)
        self.assertEqual(roll.pins_knocked_down, 10)
        self.assertEqual(roll.roll_number, 3)
