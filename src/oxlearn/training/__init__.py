import random

from oxlearn.play import play_game as _play_game
from oxlearn.board import BoardSymbol as _BoardSymbol

from oxlearn.training.learnplayer import TrainedPlayer
from oxlearn.training.learnplayer import LearnPlayerBrain
from oxlearn.training.learnplayer import LearnPlayer


def training_routine(
    n_games: int, brain: LearnPlayerBrain, **create_player_args
) -> None:
    player_o = LearnPlayer(_BoardSymbol.O, brain=brain, **create_player_args)
    player_x = LearnPlayer(_BoardSymbol.X, brain=brain, **create_player_args)

    for n in range(n_games):
        _play_game(player_o, player_x)

    brain.save()
