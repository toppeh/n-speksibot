from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext
from telegram import Update, TelegramError
import json
import config

# name|chat_id
groups = dict()

with open('groups.txt') as f:
    groups = json.load(f)
    f.close()


def addGroup(update: Update, context: CallbackContext):
    for chatName in groups:
        if groups[chatName] == update.message.chat_id:
            context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Ryhmä on jo lisätty nimellä {chatName}')
            return
    name = update.message.text[10:]
    groups[name] = update.message.chat_id
    with open('groups.txt', 'w') as fp:
        json.dump(groups, fp)
        fp.close()
    context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Ryhmä lisätty nimellä {name}')


def printGroups(update: Update, context: CallbackContext):
    names = list(groups.keys())
    names.sort()
    str = ', '.join(names)
    if len(str) > 0:
        context.bot.sendMessage(chat_id=update.message.chat_id, text=str)
    else:
        context.bot.sendMessage(chat_id=update.message.chat_id, text='Yhtään ryhmää ei ole vielä lisätty')


def forwardMsg(update: Update, context: CallbackContext):
    if update.message.text[0] != '@':
        return
    strTuple = update.message.text.partition(' ')
    if len(strTuple[1]) == 0:
        return
    if strTuple[0][1:] not in groups:
        context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Ryhmää nimeltä {strTuple[0][1:]} ei löytynyt.'
                                                                     f' Klikkaa /list näkeäksesi listan tietämistäni'
                                                                     f' ryhmistä')
        return
    try:
        context.bot.forwardMessage(chat_id=groups[strTuple[0][1:]], from_chat_id=update.message.chat_id,
                                   message_id=update.message.message_id)
    except TelegramError:
        context.bot.sendMessage(chat_id=update.message.chat_id, text='Jokin meni pieleen :/')


updater = Updater(token=config.TOKENN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('addgroup', addGroup))
dispatcher.add_handler(CommandHandler('list', printGroups))
dispatcher.add_handler(MessageHandler(Filters.text, forwardMsg))

updater.start_polling()
