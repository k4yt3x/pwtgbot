#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: PWSearch Groupchat Bot
Author: K4YT3X
Date Created: June 19, 2021
Last Modified: June 25, 2021

(C) 2021 K4YT3X
All rights reserved.
"""

# fmt: off
# monkey patch gevent before ssl is imported
from gevent import monkey
monkey.patch_all()
# fmt: on

# built-in imports
import argparse
import os
import pathlib
import sys

# third-party imports
from bs4 import BeautifulSoup
from loguru import logger
from pwsearch import Pwsearch
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


# configuration file path
SECRET_PATH = pathlib.Path("/run/secrets/pwtgbot")

# help message, pretty apparent
HELP_MESSAGE = """歡迎使用 PwnWiki 搜索 Bot
語法: /pwsearch 最大結果數量 關鍵詞1 關鍵詞2 ...
例：/pwsearch 5 internet explorer"""


def parse_arguments() -> argparse.Namespace:
    """parse command line arguments

    Returns:
        argparse.Namespace: parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        prog="pwtgbot", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # serve command
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        help="maximum number of entries to search for",
        default=20,
    )

    return parser.parse_args()


def chunks(lst: list, n: int) -> list:
    """yield successive n-sized chunks from lst

    Args:
        lst (list): input list
        n (int): chunk size

    Yields:
        list: evenly split chunks
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def start(update: Update, context: CallbackContext) -> None:
    """start and help command handler

    Args:
        update (Update): telegram Update object (provided by dispatcher)
        context (CallbackContext): telegram CallbackContext object (provided by dispatcher)
    """
    update.message.reply_text(HELP_MESSAGE)


def pwsearch(update: Update, context: CallbackContext) -> None:
    """search PwnWiki for keywords and reply the message with the search results

    Args:
        update (Update): telegram Update object (provided by dispatcher)
        context (CallbackContext): telegram CallbackContext object (provided by dispatcher)
    """
    global limit

    # return if not a regular message
    if update.message is None:
        return

    logger.info(f"Received arguments: {context.args}")

    # if not enough arguments are given
    #   print help and return
    if len(context.args) < 2:
        start(update, context)
        return

    # create MediaWiki instance for PwnWiki
    pwsearch = Pwsearch()

    try:
        # this will trigger ValueError if invalid
        results = pwsearch.search(context.args[1:], max_results=int(context.args[0]))

        if int(context.args[0]) <= 0:
            raise ValueError("arg0 must must > 0")

        if int(context.args[0]) > limit:
            update.message.reply_text(f"爲防止濫用，最大搜索上限爲 {limit} 條")
            return

        if len(results) == 0:
            update.message.reply_text("沒有找到結果，請修改關鍵詞後重試")
            return

        else:
            logger.info(f"Found {len(results)} results")

            # asynchronously fetch page details
            logger.info("Retrieving information for pages")
            pages = pwsearch.pages(titles=results)

            replies = []
            omitted_translations = 0
            for (index, page) in enumerate(pages):

                result = results[index]

                # send reply message
                logger.info(f"Sending reply for page {result}")
                if page is None:
                    if result.startswith("Translations:"):
                        omitted_translations += 1
                    else:
                        replies.append(
                            "• <a href='{}'>{}</a>".format(
                                "None", page.get("displaytitle", result)
                            )
                        )
                else:
                    title = page.get("displaytitle", result)

                    # if title contains HTML, use result
                    if BeautifulSoup(title, "html.parser").find():
                        title = result

                    if title.startswith("Translations:"):
                        omitted_translations += 1
                    else:
                        replies.append(
                            "• <a href='{}'>{}</a>".format(page["url"], title)
                        )

            # send a maximum of 60 entries at a time
            reply_chunks = list(chunks(replies, 50))
            index = 0

            while index < len(reply_chunks) - 1:
                update.message.reply_html(
                    "\n".join(reply_chunks[index]), disable_web_page_preview=True
                )
                index += 1

            update.message.reply_html(
                "\n".join(reply_chunks[-1])
                + "\n檢索結果：{}\n已忽略的翻譯頁面：{}".format(len(results), omitted_translations),
                disable_web_page_preview=True,
            )

    except ValueError:
        update.message.reply_text(f"無效輸入：{context.args[0]}")

    except Exception as e:
        logger.exception(f"Program has encountered an error: {e}")
        update.message.reply_text("程式錯誤")


def error_handler(update: object, context: CallbackContext) -> None:
    """custom exception handler

    Args:
        update (Update): telegram Update object (provided by dispatcher)
        context (CallbackContext): telegram CallbackContext object (provided by dispatcher)
    """
    logger.error(context.error)


def main() -> int:
    """program entry point

    Returns:
        int: 0 if successful, else 1
    """

    global limit
    args = parse_arguments()
    limit = args.limit

    try:
        if SECRET_PATH.is_file():
            with SECRET_PATH.open("r") as secret_file:
                secret = secret_file.read().strip()
        elif os.environ.get("PWTGBOT_SECRET"):
            secret = os.environ["PWTGBOT_SECRET"]
        else:
            logger.critical("Unable to find telegram bot secret")
            return 1

        logger.info("Initializing bot instance")
        updater = Updater(secret)

        # register dispatcher and message handlers
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", start))
        dispatcher.add_handler(CommandHandler("pwsearch", pwsearch))

        # use custom error handler
        dispatcher.add_error_handler(error_handler)

        logger.info("Starting to poll")
        updater.start_polling()

        # start_polling() is non-blocking
        # idle() makes the main thread alive until ^C or SIGINT/SIGTERM
        updater.idle()
        return 0

    # upon receiving stop signals, exit without errors
    except (KeyboardInterrupt, SystemExit):
        return 0

    # if the worker wasn't able to catch the error
    #   the problem is critical
    except Exception as e:
        logger.exception(f"Program has encountered a critical error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
