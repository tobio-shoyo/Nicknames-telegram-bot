#!python3


import os.path
import pickle
import datetime
import configparser
import logging
import sys

from telegram.ext import Updater, CommandHandler
from telegram import error


def load_settings():
    global settings
    if not os.path.exists('bot_settings.ini'):
        logging.error('FAILED TO FIND SETTING FILE!')
        sys.exit('FAILED TO FIND SETTING FILE!')
    else:
        config = configparser.ConfigParser()
        config.read('bot_settings.ini')
        settings = config['BOT']


def load_groups():
    global commands
    default = {'everyone': ['@user1',
                            '@user2',
                            '@user3',
                            '@user4'],
               'nickname1': ['@user1', '@user2']}

    try:
        with open(r"groupNames.p", "rb") as input_file:  # get the current data from the pickle file
            commands = pickle.load(input_file)
        logging.info('Pickle file loaded')
    except FileNotFoundError:
        with open(r"groupNames.p", "wb") as output_file:
            pickle.dump(default, output_file)
        logging.info('Pickle file created with default values')
        commands = default


def nickname_reply(update, context):
    """
    Function that receives message and context
    deletes the "call message" and replies instead
    """
    asked_nickname = update.message.text[1:]   # Get only the command name since commands in telegram start with '/'
    asked_nickname = asked_nickname.replace(' ' + ' '.join(context.args), '')   # Remove any args from the text
    asked_nickname = asked_nickname.replace('@OurUf_bot' + ' '.join(context.args), '')
    names = commands[asked_nickname]    # Get the actual tags for every nickname
    try:
        names.remove('@' + update.message.from_user.username)  # Remove the sender from the tag list
    except ValueError:
        pass    # The sender is not part of the group, so no need to remove him(obviously)
    tags = ' '.join(names)

    # get the message to reply to
    sender = update.message.from_user.first_name
    if len(context.args) > 0:
        tags = ' '.join(context.args) + '\n' + tags
    if update.message.reply_to_message is not None:
        message_to_reply = update.message.reply_to_message.message_id
        # delete the reply
        try:    # Try to delete the message. == If you have permissions to do so
            if settings['WITH_DELETE'].lower() == 'true':
                context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        except error.BadRequest:
            logging.debug('No permission to delete message')
        # create new message
        try:
            update.message.reply_text('{}:  {}'.format(sender, tags), reply_to_message_id=message_to_reply)
        except Exception:
            update.message.reply_text(tags)
    else:  # If the message is not a reply
        # delete the reply
        try:  # Try to delete the message. == If you have permissions to do so
            if settings['WITH_DELETE'].lower() == 'true':
                context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        except error.BadRequest:
            logging.debug('No permission to delete message')
        # create new message
        context.bot.send_message(update.message.chat_id, text='{}:  {}'.format(sender, tags))


def get_group(update, context):
    if len(context.args) == 1:
        try:
            context.bot.send_message(chat_id=update.message.chat_id, text=' '.join(commands.get(context.args[0])))
        except TypeError:
            logging.debug("Couldn't get this group's contents")
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='This command takes 1 argument!\nExample: get_group_members groupName')


def replace_member(update, context):
    if len(context.args) == 3:
        member_tag = context.args[1]
        try:
            commands[context.args[0]].remove(member_tag)
            commands[context.args[0]].append(context.args[2])
            with open(r"groupNames.p", "wb") as output_file:
                pickle.dump(commands, output_file)
                logging.info('[{}] Changed: {} to {} in: {}'.format(str(datetime.datetime.now()), context.args[1],
                                                             context.args[2], context.args[0]))
        except ValueError:  # If the member we're trying to remove isn't in that group
            context.bot.send_message(chat_id=update.message.chat_id, text='Could\'t replace member!')
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='This command takes 3 arguments!\nExample: replaceMember everyone @user @user')


def add_group(update, context):
    if len(context.args) >= 2:
        if context.args[0] not in commands:
            new_item_list = []
            for item in range(1, len(context.args)):
                new_item_list.append(context.args[item])
            commands[context.args[0]] = new_item_list
            with open(r"groupNames.p", "wb") as output_file:
                pickle.dump(commands, output_file)
            logging.info('[{}] Group {} added! ', context.args[0])
        else:
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text='This group already exists'
                                     )
    else:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='This command takes 2+ arguments!')


def main():
    logging.basicConfig(filename='bot_logs.log', format='[%(asctime)s] - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                        level=logging.INFO)    # initialize logging module and format. exclude debug messages
    load_settings()
    load_groups()

    updater = Updater(settings['TOKEN'], use_context=True)
    for key in commands.keys():     # add nickname commands according to the dictionary (key is command name)
        updater.dispatcher.add_handler(CommandHandler(key, nickname_reply))

    updater.dispatcher.add_handler(CommandHandler('get_group', get_group))
    updater.dispatcher.add_handler(CommandHandler('replace_member', replace_member))
    updater.dispatcher.add_handler(CommandHandler('add_group', add_group))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
