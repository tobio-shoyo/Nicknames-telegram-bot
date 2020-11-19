#! Python3

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import error, Update

import os.path
import pickle
import configparser
import logging
import sys
import re
import GroupNicknames


def load_settings() -> None:
    global settings
    if not os.path.exists('bot_settings.ini'):
        logging.info('FAILED TO FIND SETTING FILE!')
        sys.exit('FAILED TO FIND SETTING FILE!')
    else:
        config = configparser.ConfigParser()
        config.read('bot_settings.ini')
        settings = config['BOT']


def load_nicknames() -> None:
    global nicknames
    default = {'everyone': ['@user1',
                            '@user2',
                            '@user3',
                            '@user4'],
               'nickname1': ['@user1', '@user2']}

    try:
        with open(r"nicknames.p", "rb") as input_file:  # get the current data from the pickle file
            nicknames = pickle.load(input_file)
        logging.info('Pickle file loaded')
    except FileNotFoundError:
        with open(r"nicknames.p", "wb") as output_file:
            pickle.dump(default, output_file)
        logging.info('Pickle file created with default values')
        nicknames = default


def catch_and_replace(update: Update, context: CallbackContext) -> None:
    if update.message is not None:  # only new/forwarded messages are acceptable here. := "not edited_message"
        tags_counter = 0
        full_message = update.message.text  # Strip off the '@' char at the beginning of the nickname call
        tag_message = ''
        at_regex = re.compile(r'@\w*')   # get all nicknames in the message
        nickname = at_regex.findall(full_message)

        for item in nickname:   # check for multiple nicknames in a message
            if item[1:] in nicknames:   # assuming all nicknames are without '@'. We need to strip it to get it in dic'
                tags_counter += 1
                tag_message += ' '.join(nicknames[item[1:]])    # add all relevant tags to the message to be send
                tag_message += ' '
        if tags_counter > 0:
            update.message.reply_text(tag_message,
                                      reply_to_message_id=update.message.message_id)  # send the tags as a reply


def add_nickname(update, context):
    global nicknames
    if len(context.args) >= 2:
        if context.args[0] not in nicknames:
            new_item_list = []
            for item in range(1, len(context.args)):
                new_item_list.append(context.args[item])
            nicknames[context.args[0]] = new_item_list
            with open(r"nicknames.p", "wb") as output_file:
                pickle.dump(nicknames, output_file)
            logging.info('Nickname {} added! '.format(context.args[0]))
        else:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='This nickname already exists')
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='This command takes 2+ arguments!')


def delete_nickname(update, context):
    global nicknames
    if len(context.args) == 1:
        if context.args[0] in nicknames:
            del nicknames[context.args[0]]
            with open(r"nicknames.p", "wb") as output_file:
                pickle.dump(nicknames, output_file)
            logging.info('Nickname {} removed! '.format(context.args[0]))
        else:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='No such nickname')
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='This command takes 1 argument!')


def get_group_nicknames(update, context):
    global nicknames
    chat_id = update.message.chat_id
    message_to_send = ''

    for item in nicknames:
        message_to_send += ' {} - {}\n'.format(item, " ".join(nicknames[item]))

    context.bot.send_message(chat_id=chat_id, text=message_to_send)


def add_to_nickname(update, context):
    global nicknames
    added = ''
    if len(context.args) >= 2:
        if context.args[0] in nicknames:
            for nick in range(1, len(context.args)):    # start from 1, because 0 is the nickname itself
                    nicknames[context.args[0]].append(context.args[nick])
                    added += ' {}'.format(context.args[nick])
            with open(r"nicknames.p", "wb") as output_file:
                pickle.dump(nicknames, output_file)
            logging.info('Nicknames {} added to {}'.format(added, context.args[0]))
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text='No such nickname')
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text='Too little arguments')


def main() -> None:
    # NOTE: Currently logging into stdout! Will be changed later!
    logging.basicConfig(format='[%(asctime)s] - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                        level=logging.INFO)  # initialize logging module and format. exclude debug messages
    load_settings()
    load_nicknames()
    updater = Updater(settings['TOKEN'], use_context=True)
    updater.dispatcher.add_handler(MessageHandler(Filters.regex('.*@.*') & ~Filters.command, catch_and_replace))
    updater.dispatcher.add_handler(CommandHandler('add_nickname', add_nickname))
    updater.dispatcher.add_handler(CommandHandler('delete_nickname', delete_nickname))
    updater.dispatcher.add_handler(CommandHandler('get_nicknames', get_group_nicknames))
    updater.dispatcher.add_handler(CommandHandler('add_to_nickname', add_to_nickname))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    global settings
    global nicknames
    main()
