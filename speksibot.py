from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext
from telegram import Update, TelegramError
import json
import config
from random import choice

# name|chat_id
groups = dict()
users = dict() # user_id: username

with open('groups.json') as f:
    groups = json.load(f)
    f.close()


def writeToFile():
    with open('groups.txt', 'w') as fp:
        json.dump(groups, fp)
        fp.close()


def addGroup(update: Update, context: CallbackContext):
    name = update.message.text[10:]
    if ' ' in name:
        context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Ryhmän nimessä ei saa olla välilyöntiä.')
        return
    for chatName in groups:
        if groups[chatName] == update.message.chat_id:
            context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Ryhmä on jo lisätty nimellä {chatName}')
            return
        if chatName == name:
            context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Ryhmä nimeltä {chatName} on jo lisätty')
            return
    groups[name] = update.message.chat_id
    writeToFile()
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
    name = update.message.parse_entity(update.message.entities[0])[1:]
    if name in groups:
        try:
            context.bot.forwardMessage(chat_id=groups[name], from_chat_id=update.message.chat_id,
                                       message_id=update.message.message_id)
            context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Viesti välitetty.')
        except TelegramError:
            #context.bot.sendMessage(chat_id=update.message.chat_id, text='Jokin meni pieleen :/')
            pass

def replyForward(update: Update, context: CallbackContext):
    name = update.message.parse_entity(update.message.entities[0])[1:]
    if name in groups:
        try:
            context.bot.forward_message(chat_id=groups[name], from_chat_id=update.message.chat_id,
                                        message_id=update.message.reply_to_message.message_id)
        except TelegramError:
            #context.bot.sendMessage(chat_id=update.message.chat_id, text='Jokin meni pieleen :/')
            pass


def changeName(update: Update, context: CallbackContext):
    newName = update.message.text[12:]
    if ' ' in newName:
        context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Ryhmän nimessä ei saa olla välilyöntiä.')
        return
    elif newName in groups.keys():
        context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Nimi on jo käytössä.')
        return
    elif len(newName) == 0:
        context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Uusi nimi ei saa olla tyhjä')
        return
    for name, id in groups.items():
        if id == update.message.chat_id:
            groups[newName] = update.message.chat_id
            del groups[name]
            writeToFile()
            context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Nimi vaihdettu.')
            return
    # The group has not been added yet so might as well add it here
    groups[newName] = update.message.chat_id
    writeToFile()
    context.bot.sendMessage(chat_id=update.message.chat_id, text=f'Ryhmä lisätty.')


def help(update: Update, context: CallbackContext):
    helpText = f'Lisää ryhmä: /addgroup <nimi>\n' \
        f'Vaihda tämän ryhmän nimeä: /changename <uusi_nimi>\n' \
        f'Listaa kaikki ryhmät: /list\n' \
        f'Välitä viesti toiselle viestille: @ryhmä viestisi'
    context.bot.sendMessage(chat_id=update.message.chat_id, text=helpText)

def chatMemberLister(update: Update, context: CallbackContext):
    if update.message.chat.type != 'private':
        pass
    users[update.message.from_user.id] = update.message.from_user.username

def joku(update: Update, context: CallbackContext):
    if len(users) == 0:
        return
    user = choice(list(users.keys()))
    context.bot.send_message(chat_id=update.message.chat_id,
                            text=f'@{users[user]} voisi')

updater = Updater(token=config.TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('addgroup', addGroup))
dispatcher.add_handler(CommandHandler('list', printGroups))
dispatcher.add_handler(CommandHandler('changename', changeName))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(MessageHandler(Filters.reply & Filters.entity('mention'), replyForward))
dispatcher.add_handler(MessageHandler(Filters.entity('mention'), forwardMsg))
dispatcher.add_handler(MessageHandler(Filters.regex('joku'), joku))
dispatcher.add_handler(MessageHandler(Filters.text, chatMemberLister))

updater.start_polling()
