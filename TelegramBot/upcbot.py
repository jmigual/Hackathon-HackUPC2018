# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Basic example for a bot that uses inline keyboards.

# This program is dedicated to the public domain under the CC0 license.
"""
import logging
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Bot, Update, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from emoji import emojize

import avla
import timetable

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

DONUT_PARROT = 'CgADBAADwgMAAiRlWVKCtPYHjtSx-QI'
PARTY_PARROT = 'CgADBAADxgMAAiRlWVK7Oa85OWrCqAI'

selected_semester = {}
courses_program = re.compile(r"(\w+(?: *, *\w+)*)")


def get_healthy(bot: Bot, update: Update):
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Sports options", callback_data="sports")],
        [InlineKeyboardButton("UPC Cardio", callback_data="cardio")],
    ])
    update.message.reply_text(reply_markup=reply_markup, parse_mode="MARKDOWN",
                              text="By promoting a healthy life, individuals can have a bigger control over their "
                                   "health and thus improve it. This is an evolutionary concept which comprises "
                                   "lifestyles and other social and environmental factors.\n\n"
                                   "This helps individuals to strengthen their skills and capabilities.\n\n"
                                   "_Select an option to see more information regarding health options at UPC_")


def get_lab(bot: Bot, update: Update):
    # query = update.callback_query
    chat_id = update.message.chat.id
    bot.send_chat_action(chat_id, ChatAction.TYPING)

    labs = avla.get_lab_buildings()
    line = [InlineKeyboardButton(lab, callback_data=lab) for lab in labs]
    reply_markup = InlineKeyboardMarkup([line])
    update.message.reply_text('Please choose a lab:', reply_markup=reply_markup)


def get_timetable(bot, update: Update):
    chat_id = update.message.chat.id
    bot.send_chat_action(chat_id, ChatAction.TYPING)

    semesters = timetable.get_semesters()
    buttons = [[InlineKeyboardButton(t, callback_data=t)] for t in semesters]
    update.message.reply_text("Select the desired semester", reply_markup=InlineKeyboardMarkup(buttons))


def parse_messages(bot: Bot, update: Update):
    global selected_semester
    chat_id = update.message.chat.id

    if update.message.text.lower() == "biene":
        bot.send_animation(chat_id=chat_id, animation=PARTY_PARROT, caption="BIENE")
        return

    semester = selected_semester.get(chat_id, None)
    if semester is None:
        return

    text = update.message.text
    m = courses_program.match(text)
    if not m:
        update.message.reply_text('Pattern not recognized please send it again')
        return

    courses = [s.strip() for s in m.group(1).split(",")]

    available_courses = timetable.get_available_courses(semester)
    difference = set(courses) - set(available_courses)
    if len(difference) > 0:
        update.message.reply_text(f"I do not recognize the following names: {', '.join(difference)}\n"
                                  f"Please send them again")
        return

    res = bot.send_animation(chat_id=chat_id, animation=DONUT_PARROT,
                             caption="Please wait while we search the timetables")
    bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    table = timetable.get_timetable(semester, courses, True)
    bot.delete_message(chat_id=chat_id, message_id=res.message_id)

    if len(table) <= 0:
        update.message.reply_text(emojize("Sorry! No timetable found :cry:", use_aliases=True))
        return
    update.message.reply_text("Click here to see your timetable: \n" + timetable.timetable_to_url(table))
    selected_semester[chat_id] = None


def button(bot: Bot, update: Update):
    global selected_semester
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    if query.message.text == 'Please choose a lab:':
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        res = bot.send_animation(chat_id, animation=DONUT_PARROT,
                                 caption="Please wait while we search for the available labs")
        bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        K = 25
        caption = joinStrings("Sales lliures:", "Sales ocupades:", K) + "\n"
        available, unavailable = avla.lab_stats(query.data)
        availableOutput = []
        unavailableOutput = []
        for k, i in sorted(available.items(), key=lambda kv: kv[1][0], reverse=True):
            availableOutput.append(
                "*{}*: {} {}".format(k[2:], i[0], "_(fins {})_".format(i[1]) if len(i[1]) > 0 else ""))
        for k, i in sorted(unavailable.items(), key=lambda kv: kv[1][1]):
            unavailableOutput.append(
                "*{}*: {} {}".format(k[2:], i[0], "_(fins {})_".format(i[1]) if len(i[1]) > 0 else ""))

        n_lines = max(len(availableOutput), len(unavailableOutput))
        availableOutput += [""] * (n_lines - len(availableOutput))
        unavailableOutput += [""] * (n_lines - len(unavailableOutput))
        caption += "\n".join(joinStrings(a, b, K) for a, b in zip(availableOutput, unavailableOutput))

        bot.edit_message_media(chat_id=chat_id, message_id=res.message_id,
                               media=InputMediaPhoto(avla.lab_image(query.data),
                                                     caption=caption, parse_mode="MARKDOWN"))

    elif query.message.text == 'Select the desired semester':
        selected_semester[chat_id] = query.data
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.send_message(chat_id, text="Please enter the course's IDs separated by commas")

    elif query.data == "sports":
        bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                              text="The UPC Sports Service, offers sport and health related "
                                   "activities to the university community. It gives advice for physical activities "
                                   "inside the UPC Cardio program, which intends to promote the increase of "
                                   "physical activity among its participants, since it reduces the risk of "
                                   "cardiovascular diseases.\n\nYou can find more information at the website:\n"
                                   "https://www.upc.edu/esports")
    elif query.data == "cardio":
        new_reply = InlineKeyboardMarkup([
            [InlineKeyboardButton("Healthy habits", callback_data="healthy_habits")],
            [InlineKeyboardButton("Cardio friendly restaurants", callback_data="cardio_restaurants")],
        ])
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, reply_markup=new_reply, parse_mode="MARKDOWN",
                              text="UPC offers multiple programs to reduce the risk of cardiovascular diseases. Among"
                                   "those there are:\n"
                                   " - *Healthy habits* to improve your life\n"
                                   " - *Cardio friendly bars and restaurants* that have been aproved for their healthy "
                                   "menu\n\n_Select an option to receive more information_")

    elif query.data == "healthy_habits":
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, parse_mode="MARKDOWN",
                              text="Healthy habits can prevent the appearance of risk factors for cardiovascular "
                                   "diseases, and in the same way inadequate eating habits, along with other "
                                   "factors such as a sedentary lifestyle, somking or stress, can facilitate "
                                   "the development of these disorders. See information for:\n"
                                   " - [Nutritional habits](https://www.upc.edu/prevencio/ca/promocio-salut/"
                                   "upc-cardio/canvi-habits/alimentacio)\n"
                                   " - [Toxic habits](https://www.upc.edu/prevencio/ca/promocio-salut/"
                                   "upc-cardio/canvi-habits/tabac)\n"
                                   " - [Physical habits](https://www.upc.edu/prevencio/ca/promocio-salut/"
                                   "upc-cardio/canvi-habits/activitat-fisica)")
    elif query.data == "cardio_restaurants":
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, parse_mode="MARKDOWN",
                              text="At UPC there are bars and restaurants that are accredited by the [Public Health "
                                   "Agency of Catalonia](http://www.amed.cat/home.php) in the framework of the "
                                   "Mediterranean food, a diet that is cardio-healthy.\n\n_More information at:_\n"
                                   "https://www.upc.edu/prevencio/ca/promocio-salut/upc-cardio/bars-restaurants")


def help(bot, update):
    text = ("Welcome to the UPC bot. The aim of this bot is to help you find more information "
            "regarding availability of computer laboratories, the current semester timetables "
            "or learning about healthy options to maintain a healthy life. You can use the "
            "following commands:\n\n"
            " - /help: Show this help\n"
            " - /get\_lab: Get information regarding available computer labs' spaces\n"
            " - /get\_timetable: Get a timetable for your courses during this semester\n"
            " - /get\_healthy: Learn about the options that can help you have a better and "
            "safer cardiovascular life\n\n"
            "_Also you can find our easter eggs_ :flushed_face::egg:")

    update.message.reply_text(parse_mode="MARKDOWN", text=emojize(text, use_aliases=False))


def biene(bot, update: Update):
    bot.send_animation(chat_id=update.message.chat.id, animation=PARTY_PARROT, caption="BIENE")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("771476950:AAGTRsrT7Sewj9RxtJevOi5mnM4heM5GR4k")

    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('start', help))
    updater.dispatcher.add_handler(CommandHandler('biene', biene))
    updater.dispatcher.add_handler(CommandHandler('get_lab', get_lab))
    updater.dispatcher.add_handler(CommandHandler("get_timetable", get_timetable))
    updater.dispatcher.add_handler(CommandHandler("get_healthy", get_healthy))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, parse_messages))

    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


def joinStrings(a, b, n):
    return a + " " * (n - len(a)) + b


if __name__ == '__main__':
    main()
