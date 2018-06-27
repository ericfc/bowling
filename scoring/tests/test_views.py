from django.test import TestCase
from unittest.mock import patch
from rest_framework.test import APIRequestFactory

from scoring.models import (
    Frame,
    Game,
    Player,
    Roll
)
from scoring.views import GameListCreateAPIView, RollCreateAPIView


class GameListCreateAPIViewTestCase(TestCase):
    def test_post(self):
        """
        Test post, the creation of a new Game
        """

        response = self.client.post(
            '/games/', {'player_names': ['player_name']}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(Player.objects.filter(name='player_name').count(), 1)
        self.assertEqual(
            Frame.objects.filter(player__name='player_name').count(), 10
        )


class RollCreateAPIViewTestCase(TestCase):
    def setUp(self):
        self.game = Game.objects.create()
        self.player = Player.objects.create(game=self.game, name='player_name')
        self.frame = Frame.objects.create(player=self.player, frame_number=1)

    @patch.object(Game, 'update_is_ongoing')
    @patch.object(Player, 'make_roll')
    def test_post(self, mock_make_roll, mock_update_is_ongoing):
        """
        Test the creation of a new Roll
        """
        mock_make_roll.return_value = Roll(
            frame=self.frame, pins_knocked_down=10, roll_number=1, id=1
        )

        response = self.client.post(
            '/games/1/roll/', {'player_id': 1, 'pins_knocked_down': 10}
        )

        self.assertEqual(
            response.data, {'id': 1, 'roll_number': 1, 'pins_knocked_down': 10}
        )
        mock_update_is_ongoing.assert_called_once_with()

    @patch.object(Player, 'make_roll')
    def test_post_invalid(self, mock_make_roll):
        """
        Test creating Roll in invalid scenarios
        """
        mock_make_roll.return_value = None

        response = self.client.post(
            '/games/111/roll/', {'player_id': 1, 'pins_knocked_down': 10}
        )

        self.assertEqual(
            response.data, {'detail': 'Game with id 111 not found'}
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.post(
            '/games/1/roll/', {'player_id': 111, 'pins_knocked_down': 10}
        )
        self.assertEqual(
            response.data, {'detail': 'Player with id 111 not found.'}
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.post(
            '/games/1/roll/', {'player_id': 1, 'pins_knocked_down': 10}
        )
        self.assertEqual(
            response.data,
            {'detail': 'player_name has exhausted all their rolls'}
        )
        self.assertEqual(response.status_code, 400)
