from django.test import SimpleTestCase, TestCase

from scoring.models import Game, Player
from scoring.serializers import (
    CreateGameSerializer,
    CreateRollSerializer,
    GameSerializer,
    RollSerializer,
    PlayerSerializer,
)


class CreateGameSerializerTestCase(TestCase):
    def test_validation(self):
        """
        Test data validation
        """
        data = {'player_names': ['test_name']}
        serializer = CreateGameSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        data = {'invalid': ['not_valid']}
        serializer = CreateGameSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create(self):
        """
        Test the creation of a Game, the Players, and Frames
        """
        data = {'player_names': ['test_name']}
        serializer = CreateGameSerializer(data=data)
        serializer.is_valid()
        game = serializer.create(serializer.validated_data)
        player = game.players.first()

        self.assertEqual(game.players.count(), 1)
        self.assertEqual(player.name, 'test_name')
        self.assertEqual(player.frames.count(), 10)


class CreateRollSerializerTestCase(SimpleTestCase):
    def test_validation(self):
        """
        Test data validation
        """
        data = {'player_id': 1, 'pins_knocked_down': 1}
        serializer = CreateRollSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        data = {'player_id': 0, 'pins_knocked_down': 11}
        serializer = CreateRollSerializer(data=data)
        self.assertFalse(serializer.is_valid())

