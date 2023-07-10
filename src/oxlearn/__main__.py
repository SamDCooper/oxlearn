import argparse
import colorama
import datetime
import logging
import random

from oxlearn import __version__
from oxlearn.board import Board
from oxlearn.board import BoardSymbol
from oxlearn.play import IPlayer
from oxlearn.play import play_game
from oxlearn.randomplayer import RandomPlayer
from oxlearn.training import LearnPlayer
from oxlearn.training import LearnPlayerBrain
from oxlearn.training import TrainedPlayer
from oxlearn.training import training_routine

logger = logging.getLogger("oxlearn")


class HumanPlayer(IPlayer):
    def __init__(self, symbol: BoardSymbol, **kwargs):
        super().__init__(symbol, **kwargs)

    def colored_symbol(self, symbol: BoardSymbol, pos) -> str:
        prefix = (
            colorama.Style.RESET_ALL
            if symbol is None
            else (colorama.Fore.GREEN if symbol == self.symbol else colorama.Fore.RED)
        )
        symbol_str = str(pos) if symbol is None else str(symbol)
        return f"{prefix}{symbol_str}"

    def print_board(self, board: Board, with_numbers: bool):
        positions = {} if with_numbers else None
        counter = 1 if with_numbers else None
        lines = []
        line = []
        for pos in Board.all_positions():
            v = board[pos]
            line.append(self.colored_symbol(v, pos))
            if (pos + 1) % Board.width == 0:
                lines.append(" ".join(line))
                line = []
        print("\n".join(lines), colorama.Style.RESET_ALL)

    def move(self, board: Board) -> int:
        self.print_board(board, with_numbers=True)
        options = board.available_positions

        next_pos = None
        while next_pos is None:
            inp = input(
                f"Your move, {self.symbol}. Enter a number position from above or press"
                " enter to concede.\n>"
            )
            if inp == "":
                return None

            try:
                int_inp = int(inp)
                if int_inp in options:
                    next_pos = int_inp
                else:
                    print(f"Value must be a free position from the above board.")
            except ValueError:
                print(f"Value must be a free position from the above board.")
        return next_pos

    def notify_win(self, board: Board) -> None:
        self.print_board(board, with_numbers=False)
        print(f"Congratulations {self.symbol}! You win!")

    def notify_loss(self, board: Board) -> None:
        self.print_board(board, with_numbers=False)
        print(f"Sorry {self.symbol}! You lose!")

    def notify_draw(self, board: Board) -> None:
        self.print_board(board, with_numbers=False)
        print("It's a draw!")


def parse_args(available_players: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="oxlearn", description="Simple machine learning tic tac toe program"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--training",
        action="store",
        type=int,
        help=(
            "Training mode. Overrides player-o and player-x to run the specified number"
            " of training rounds"
        ),
    )
    parser.add_argument(
        "--player-o",
        choices=available_players,
        default="human",
        help="Sets which player is player O. Player O always goes first",
    )
    parser.add_argument(
        "--player-x",
        choices=available_players,
        default="trained",
        help="Sets which player is player X. Player X always goes second",
    )
    parser.add_argument(
        "--seed",
        action="store",
        type=int,
        help="Set the seed for random number generation",
    )
    parser.add_argument(
        "--logfile", action="store", type=str, help="Log the run to file"
    )
    parser.add_argument(
        "--logformat",
        action="store",
        type=str,
        default="%(asctime)s [%(levelname)s]: %(message)s",
        help="Format to pass to logging module",
    )
    parser.add_argument(
        "--loglevel",
        choices=["INFO", "WARNING", "ERROR"],
        default="WARNING",
        help="Minimum level to log",
    )
    parser.add_argument(
        "--training-input",
        action="store",
        type=str,
        default="trainingdata.json",
        help="File to use as input for training data",
    )
    parser.add_argument(
        "--training-output",
        action="store",
        type=str,
        default="trainingdata.json",
        help="File to use as output for training data. Training mode only",
    )
    parser.add_argument(
        "--exploration-rate",
        action="store",
        type=float,
        default=0.3,
        help=(
            "Exploration rate 0-1. Determines how often the learning player will try a"
            " random move. Training mode only"
        ),
    )
    parser.add_argument(
        "--learn_rate",
        action="store",
        type=float,
        default=0.2,
        help=(
            "Learning rate 0-1. Determines how much weight to give to a win or loss at"
            " learn time. Training mode only"
        ),
    )
    parser.add_argument(
        "--decay_rate",
        action="store",
        type=float,
        default=0.9,
        help=(
            "Decay rate 0-1. Determines how important entries further back in the"
            " history of a game were for learning purposes. Training mode only"
        ),
    )
    parser.add_argument(
        "--o-reward-win",
        action="store",
        type=float,
        default=1.0,
        help="Amount of 'reward' to give player O on a win. Training mode only",
    )
    parser.add_argument(
        "--o-reward-loss",
        action="store",
        type=float,
        default=0.0,
        help="Amount of 'reward' to give player O on a loss. Training mode only",
    )
    parser.add_argument(
        "--o-reward-draw",
        action="store",
        type=float,
        default=0.1,
        help="Amount of 'reward' to give player O on a draw. Training mode only",
    )
    parser.add_argument(
        "--x-reward-win",
        action="store",
        type=float,
        default=1.0,
        help="Amount of 'reward' to give player X on a win. Training mode only",
    )
    parser.add_argument(
        "--x-reward-loss",
        action="store",
        type=float,
        default=0.0,
        help="Amount of 'reward' to give player X on a loss. Training mode only",
    )
    parser.add_argument(
        "--x-reward-draw",
        action="store",
        type=float,
        default=0.5,
        help="Amount of 'reward' to give player X on a draw. Training mode only",
    )
    return parser.parse_args()


def main() -> None:
    start_time = datetime.datetime.now()
    
    available_players = {
        "human": HumanPlayer,
        "random": RandomPlayer,
        "trained": TrainedPlayer,
        "learn": LearnPlayer,
    }

    args = parse_args(list(available_players.keys()))

    if args.seed is not None:
        random.seed(args.seed)

    if args.logfile is not None:
        handler = logging.FileHandler(args.logfile)
        handler.setFormatter(logging.Formatter(args.logformat))
        logger.addHandler(handler)
        logger.setLevel(logging.getLevelName(args.loglevel))
    logger.info("----------------------------------------------------------------")
    logger.info("New session start. Cmd line params given:")
    for arg, val in vars(args).items():
        if val is not None:
            logger.info("%s = %s", arg, str(val))

    brain = LearnPlayerBrain(args.training_input, args.training_output)
    create_player_args = {
        "brain": brain,
        "exploration_rate": args.exploration_rate,
        "learn_rate": args.learn_rate,
        "decay_rate": args.decay_rate,
        "o_reward_win": args.o_reward_win,
        "o_reward_loss": args.o_reward_loss,
        "o_reward_draw": args.o_reward_draw,
        "x_reward_win": args.x_reward_win,
        "x_reward_loss": args.x_reward_loss,
        "x_reward_draw": args.x_reward_draw,
    }

    if args.training is not None:
        training_routine(args.training, **create_player_args)
    else:
        if args.player_o != "human" and args.player_x != "human":
            print("Note that both players in this config are not human.")

        player_o = available_players[args.player_o](BoardSymbol.O, **create_player_args)
        player_x = available_players[args.player_x](BoardSymbol.X, **create_player_args)
        play_again = True
        while play_again:
            play_game(player_o, player_x)
            play_again = None
            while play_again is None:
                inp = input("Play again? (y/n)\n>")
                if inp.upper() == "Y":
                    play_again = True
                elif inp.upper() == "N":
                    play_again = False
                else:
                    print("Please enter Y or N.")
        print("Thank you for playing oxlearn.")
    logger.info("Finished execution. Total run time: %s", datetime.datetime.now() - start_time)
    logger.info("----------------------------------------------------------------")


main()
