import avla
from PIL import Image

# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Basic example for a bot that uses inline keyboards.

# This program is dedicated to the public domain under the CC0 license.
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def getLab(bot, update):
    labs = avla.get_lab_buildings()

    n = len(labs)

    line = []
    for lab in labs:
        line.append(InlineKeyboardButton(lab, callback_data=lab))

    keyboard = [line]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose a lab:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query

    if query.message.text == 'Please choose a lab:':
        K = 20
        caption = joinStrings("Sales lliures:", "Sales ocupades:", K)+"\n"
        available, unavailable = avla.lab_stats(query.data)
        availableOutput = []
        unavailableOutput = []
        for k, i in sorted(available.items(), key=lambda kv: kv[1][0], reverse=True):
            availableOutput.append("*{}*: {} _(until {})_".format(k, i[0], i[1]))
        for k, i in sorted(available.items(), key=lambda kv: kv[1][1]):
            unavailableOutput.append("*{}*: {} _(until {})_".format(k, i[0], i[1]))

        n_lines = max(len(availableOutput), len(unavailableOutput))
        availableOutput += [""] * (n_lines - len(availableOutput))
        unavailableOutput += [""] * (n_lines - len(unavailableOutput))
        caption += "\n".join(joinStrings(a, b, K) for a, b in zip(availableOutput, unavailableOutput))

        bot.send_photo(chat_id=query.message.chat_id,
                       photo=avla.lab_image(query.data),
                       caption=caption,
                       parse_mode="MARKDOWN")
        bot.delete_message(chat_id=query.message.chat_id,
                           message_id=query.message.message_id)

        # bot.edit_message_(media=avla.lab_image(query.data),
        #                      chat_id=query.message.chat_id,
        #                      message_id=query.message.message_id)


def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def biene(bot, update):
    update.message.reply_text("BIENE")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("771476950:AAGTRsrT7Sewj9RxtJevOi5mnM4heM5GR4k")

    updater.dispatcher.add_handler(CommandHandler('getLab', getLab))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('biene', biene))
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
