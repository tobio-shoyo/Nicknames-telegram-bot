#! Python3

from telegram.ext import Updater, CommandHandler

TOKEN = 'TOKEN'


commands = {'everyone': ['@OmerT',
                         '@JohnnyBeGod',
                         '@Mataniger',
                         '@YuvalMiz',
                         '@Okerbis',
                         '@DorShw',
                         '@LiadSh',
                         '@noamlol',
                         '@LeeGabay'],
            'nomer': ['@noamlol', '@OmerT'],
            'leedor': ['@LeeGabay', '@DorShw'],
            'capsi': ['@JohnnyBeGod', '@YuvalMiz']}


def nickname_reply(update, context):
    """
    Function that receives message and context
    deletes the "call message" and replies instead
    """
    asked_nickname = update.message.text.replace('/', '')   # Get only the command name (to pull out of the dictionary)
    asked_nickname = asked_nickname.replace(' ' + ' '.join(context.args), '')   # Remove any args from the text
    asked_nickname = asked_nickname.replace('@OurUf_bot' + ' '.join(context.args), '')
    names = commands[asked_nickname]    # Get the actual tags for every nickname
    try:
        names.remove('@' + update.message.from_user.username)  # Remove the sender from the tag list
    except Exception:
        None
    tags = ' '.join(names)

    # get the message to reply to
    sender = update.message.from_user.first_name
    if len(context.args) > 0:
        tags = ' '.join(context.args) + '\n' + tags
    if update.message.reply_to_message is not None:
        message_to_reply = update.message.reply_to_message.message_id
        # delete the reply
        try:    # Try to delete the message. == If you have permissions to do so
            context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        except Exception:
            None
        # create new message
        try:
            update.message.reply_text('{}:  {}'.format(sender, tags), reply_to_message_id=message_to_reply)
        except Exception:
            update.message.reply_text(tags)
    else:  # If the message is not a reply
        # delete the reply
        try:  # Try to delete the message. == If you have permissions to do so
            context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        except Exception:
            None
        # create new message
        context.bot.send_message(update.message.chat_id, text='{}:  {}'.format(sender, tags))


updater = Updater(TOKEN, use_context=True)
for key in commands.keys():     # add nickname commands according to the dictionary (key is command name)
    updater.dispatcher.add_handler(CommandHandler(key, nickname_reply))


updater.start_polling()
updater.idle()
