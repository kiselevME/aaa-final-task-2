"""
Bot for playing tic tac toe game with multiple CallbackQueryHandlers.
"""
from copy import deepcopy
from enum import Enum
import logging
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)
import os


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being
# logged
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# get token using BotFather
TOKEN = os.getenv('TG_TOKEN')

CONTINUE_GAME, FINISH_GAME = range(2)

FREE_SPACE = '.'
CROSS = 'X'
ZERO = 'O'


DEFAULT_STATE = [[FREE_SPACE for _ in range(3)] for _ in range(3)]


class Message(Enum):
    X_WON = 'X (you) won! The game is over.'
    O_WON = 'O (bot) won! The game is over.'
    NO_ONE = 'No one won! The game is over.'
    X_МOVE = 'X (your) turn! Please, put X to the free place'


def get_default_state():
    """Helper function to get default state of the game"""
    return deepcopy(DEFAULT_STATE)


def generate_keyboard(state: list[list[str]]) ->\
      list[list[InlineKeyboardButton]]:
    """Generate tic tac toe keyboard 3x3 (telegram buttons)"""
    return [
        [
            InlineKeyboardButton(state[r][c], callback_data=f'{r}{c}')
            for r in range(3)
        ]
        for c in range(3)
    ]


async def update_game_status(update: Update,
                             message: Message,
                             keyboard_state: list[list[str]],
                             finish_game: bool) -> int:
    """Displays the game update on the screen and returns the code of the
    following status"""
    keyboard = generate_keyboard(keyboard_state)
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.edit_text(message.value,
                                             reply_markup=reply_markup)
    if finish_game:
        return FINISH_GAME
    return CONTINUE_GAME


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    context.user_data['keyboard_state'] = get_default_state()
    keyboard = generate_keyboard(context.user_data['keyboard_state'])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(Message.X_МOVE.value,
                                    reply_markup=reply_markup)
    return CONTINUE_GAME


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Main processing of the game"""
    # ход пользователя
    user_col, user_row = map(int, context.match.string)
    keyboard_state = context.user_data['keyboard_state']
    keyboard_state[user_col][user_row] = CROSS
    # проверка выигрыша пользователя
    if won(keyboard_state):
        return await update_game_status(update, Message.X_WON, keyboard_state,
                                        finish_game=True)

    # ход бота
    try:
        bot_col, bot_row = bots_move(keyboard_state)
        keyboard_state[bot_col][bot_row] = ZERO
    except ValueError:
        # если все поле занято (== не можем ходить), при этом никто не победил
        return await update_game_status(update, Message.NO_ONE, keyboard_state,
                                        finish_game=True)
    # проверка выигрыша бота
    if won(keyboard_state):
        return await update_game_status(update, Message.O_WON, keyboard_state,
                                        finish_game=True)

    # выводим результат на экран и продолжаем игру
    return await update_game_status(update, Message.X_МOVE, keyboard_state,
                                    finish_game=False)


def bots_move(fields: list[list[str]]) -> tuple[int, int]:
    """Chooses where to go to the bot

    Args:
        fields (list[list[str]]): current playing field

    Returns:
        tuple[int, int]: column and row where the bot will go
    """
    free_cells = []
    for i, col in enumerate(fields):
        for j, item in enumerate(col):
            if item == FREE_SPACE:
                free_cells.append((i, j))

    # random.seed не фиксирован для устранения воспроизводимости
    if len(free_cells) > 0:
        bot_col, bot_row = random.choice(free_cells)
    else:
        raise ValueError('Нет свободных клеток!')
    return bot_col, bot_row


def won(fields: list[list[str]]) -> bool:
    """Check if crosses or zeros have won the game"""
    field_size = len(fields)
    combinations = []
    for i in range(field_size):
        # вертикали
        combinations.append([(i, j) for j in range(field_size)])
        # горизонтали
        combinations.append([(j, i) for j in range(field_size)])
    # диагонали
    combinations.append([(i, i) for i in range(field_size)])
    combinations.append([(i, field_size - 1 - i) for i in range(field_size)])

    cross_srt = field_size * CROSS
    zero_srt = field_size * ZERO
    for comb in combinations:
        comb_str = ''
        for col, row in comb:
            comb_str += fields[col][row]
        if (comb_str == cross_srt) or (comb_str == zero_srt):
            return True

    return False


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    # reset state to default so you can play again with /start
    context.user_data['keyboard_state'] = get_default_state()
    return ConversationHandler.END


def main() -> None:
    """Run the bot"""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Setup conversation handler with the states CONTINUE_GAME and FINISH_GAME
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONTINUE_GAME: [
                CallbackQueryHandler(game, pattern='^' + f'{r}{c}' + '$')
                for r in range(3)
                for c in range(3)
            ],
            FINISH_GAME: [
                CallbackQueryHandler(end, pattern='^' + f'{r}{c}' + '$')
                for r in range(3)
                for c in range(3)
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Add ConversationHandler to application that will be used for handling
    # updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
