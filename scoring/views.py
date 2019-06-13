from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.response import Response

from scoring.models import Game, Player
from scoring.serializers import (
    CreateGameSerializer,
    CreateRollSerializer,
    GameSerializer,
    RollSerializer
)


class GameListCreateAPIView(generics.ListCreateAPIView):
    queryset = Game.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        game = serializer.save()

        return Response(
            GameSerializer(game).data, status=status.HTTP_201_CREATED
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateGameSerializer

        return GameSerializer


class GameRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class RollCreateAPIView(generics.CreateAPIView):
    serializer_class = CreateRollSerializer

    def post(self, request, game_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            raise NotFound('Game with id {} not found'.format(game_id))

        try:
            player = game.players.get(id=validated_data['player_id'])
        except Player.DoesNotExist:
            raise NotFound(
                'Player with id {} not found.'.format(
                    validated_data['player_id']
                )
            )

        roll = player.make_roll(validated_data['pins_knocked_down'])
        game.update_is_ongoing()

        if roll is None:
            raise ParseError(
                '{} has exhausted all their rolls'.format(player.name)
            )

        return Response(
            RollSerializer(roll).data, status=status.HTTP_201_CREATED
        )
