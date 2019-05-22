import praw
import time
import bot
import settings

while True:
    userInput = raw_input("Type something: ")

    print bot.brain.reply(userInput, max_len=100)

