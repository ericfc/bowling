from rest_framework import serializers

from scoring.models import (
    Frame,
    Game,
    Player,
    Roll
)


class CreateGameSerializer(serializers.Serializer):
    player_names = serializers.ListField(
        child=serializers.CharField(), min_length=1
    )

    def create(self, validated_data):
        """
        Creates and returns a new Game with the corresponding Players
        and Frames
        """
        game = Game.objects.create()

        for player_name in validated_data['player_names']:
            player = Player.objects.create(game=game, name=player_name)

            frames = [
                Frame(player=player, frame_number=frame_number)
                for frame_number in range(1, 11)
            ]
            Frame.objects.bulk_create(frames)

        return game


class CreateRollSerializer(serializers.Serializer):
    player_id = serializers.IntegerField(min_value=1)
    pins_knocked_down = serializers.IntegerField(min_value=0, max_value=10)


class RollSerializer(serializers.ModelSerializer):

    class Meta:
        model = Roll
        fields = ('id', 'roll_number', 'pins_knocked_down')


class FrameSerializer(serializers.ModelSerializer):
    rolls = RollSerializer(read_only=True, many=True)

    class Meta:
        model = Frame
        fields = ('id', 'frame_number', 'rolls', 'frame_type')


class PlayerSerializer(serializers.ModelSerializer):
    frames = FrameSerializer(read_only=True, many=True)
    score = serializers.SerializerMethodField()

    def get_score(self, instance):
        """
        Get the sum of all Frame scores for Player score
        """
        frame_scores = [frame.get_score() for frame in instance.frames.all()]
        return sum(
            [
                frame_score
                for frame_score in frame_scores
                if frame_score is not None
            ]
        )

    class Meta:
        model = Player
        fields = ('id', 'name', 'frames', 'score')


class GameSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(read_only=True, many=True)

    class Meta:
        model = Game
        fields = ('id', 'is_ongoing', 'players')
