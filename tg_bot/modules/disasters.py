import html
import json
import html
import os
from typing import List, Optional

from telegram import Bot, Update, ParseMode, TelegramError
from telegram.ext import CommandHandler, run_async
from telegram.utils.helpers import mention_html

from tg_bot import dispatcher, WHITELIST_USERS, TIGER_USERS, SUPPORT_USERS, SUDO_USERS, DEV_USERS, OWNER_ID
from tg_bot.modules.helper_funcs.chat_status import whitelist_plus, dev_plus, sudo_plus
from tg_bot.modules.helper_funcs.extraction import extract_user
from tg_bot.modules.log_channel import gloggable

ELEVATED_USERS_FILE = os.path.join(os.getcwd(), 'tg_bot/elevated_users.json')


def check_user_id(user_id: int, bot: Bot) -> Optional[str]:
    if not user_id:
        return "That...is a chat! baka ka omae?"

    elif user_id == bot.id:
        return "This does not work that way."

    else:
        return None

#I added extra new lines 
disasters = """ *"Disaster Levels"*
\n*Sword Masters* - Devs who can access the bots server and can execute, edit, modify bot code. Can also manage other Disasters
\n*Raider* - Only one exists, bot owner. 
\n*Wielder* - Have super user access, can gban, manage disasters lower than them and are admins in phantom.
\n*Amateur* - Have access go globally ban users across this bot 
\n*Knights* - Same as wolves but can unban themselves if banned.
\n*Explorer* - Cannot be banned, muted flood kicked but can be manually banned by admins.
"""
# do not async, not a handler 
def send_disasters(update):
   update.effective_message.reply_text(disasters, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

@run_async
@dev_plus
@gloggable
def addsudo(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        message.reply_text("This member is already a Sudo user")
        return ""

    if user_id in SUPPORT_USERS:
        rt += "Requested HA to promote a Hacker Disaster to Dragon."
        data['supports'].remove(user_id)
        SUPPORT_USERS.remove(user_id)

    if user_id in WHITELIST_USERS:
        rt += "Requested HA to promote a Wolf Disaster to Dragon."
        data['whitelists'].remove(user_id)
        WHITELIST_USERS.remove(user_id)

    data['sudos'].append(user_id)
    SUDO_USERS.append(user_id)

    with open(ELEVATED_USERS_FILE, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + "\nSuccessfully set Disaster level of {} to Dragon!".format(user_member.first_name))

    log_message = (f"#SUDO\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@sudo_plus
@gloggable
def addsupport(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        rt += "Requested HA to deomote this Dragon to Demon"
        data['sudos'].remove(user_id)
        SUDO_USERS.remove(user_id)

    if user_id in SUPPORT_USERS:
        message.reply_text("This user is already a Support User.")
        return ""

    if user_id in WHITELIST_USERS:
        rt += "Requested HA to promote this Wolf Disaster to hacker"
        data['whitelists'].remove(user_id)
        WHITELIST_USERS.remove(user_id)

    data['supports'].append(user_id)
    SUPPORT_USERS.append(user_id)

    with open(ELEVATED_USERS_FILE, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(rt + f"\n{user_member.first_name} was added as a Hacker Disaster!")

    log_message = (f"#SUPPORT\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@sudo_plus
@gloggable
def addwhitelist(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        rt += "This member is a Dragon Disaster, Demoting to Wolf."
        data['sudos'].remove(user_id)
        SUDO_USERS.remove(user_id)

    if user_id in SUPPORT_USERS:
        rt += "This user is already a Hacker Disaster, Demoting to Wolf."
        data['supports'].remove(user_id)
        SUPPORT_USERS.remove(user_id)

    if user_id in WHITELIST_USERS:
        message.reply_text("This user is already a Wolf Disaster.")
        return ""

    data['whitelists'].append(user_id)
    WHITELIST_USERS.append(user_id)

    with open(ELEVATED_USERS_FILE, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a Wolf Disaster!")

    log_message = (f"#WHITELIST\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)} \n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@sudo_plus
@gloggable
def addtiger(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        rt += "This member is a Dragon Disaster, Demoting to Tiger."
        data['sudos'].remove(user_id)
        SUDO_USERS.remove(user_id)

    if user_id in SUPPORT_USERS:
        rt += "This user is already a hacker Disaster, Demoting to Tiger."
        data['supports'].remove(user_id)
        SUPPORT_USERS.remove(user_id)

    if user_id in WHITELIST_USERS:
        rt += "This user is already a Wolf Disaster, Demoting to Tiger."
        data['whitelists'].remove(user_id)
        WHITELIST_USERS.remove(user_id)

    if user_id in TIGER_USERS:
        message.reply_text("This user is already a Tiger.")
        return ""

    data['tigers'].append(user_id)
    TIGER_USERS.append(user_id)

    with open(ELEVATED_USERS_FILE, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a Tiger Disaster!")

    log_message = (f"#TIGER\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)} \n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@dev_plus
@gloggable
def addtiger(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        rt += "This member is a Dragon Disaster, Demoting to Tiger."
        data['sudos'].remove(user_id)
        SUDO_USERS.remove(user_id)

    if user_id in SUPPORT_USERS:
        rt += "This user is already a Hacker Disaster, Demoting to Tiger."
        data['supports'].remove(user_id)
        SUPPORT_USERS.remove(user_id)

    if user_id in WHITELIST_USERS:
        rt += "This user is already a Wolf Disaster, Demoting to Tiger."
        data['whitelists'].remove(user_id)
        WHITELIST_USERS.remove(user_id)

    if user_id in TIGER_USERS:
        message.reply_text("This user is already a Tiger.")
        return ""

    data['tigers'].append(user_id)
    TIGER_USERS.append(user_id)

    with open(ELEVATED_USERS_FILE, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a Tiger Disaster!")

    log_message = (f"#TIGER\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)} \n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@dev_plus
@gloggable
def removesudo(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        message.reply_text("Requested HA to demote this user to Civilian")
        SUDO_USERS.remove(user_id)
        data['sudos'].remove(user_id)

        with open(ELEVATED_USERS_FILE, 'w') as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (f"#UNSUDO\n"
                       f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                       f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

        if chat.type != 'private':
            log_message = "<b>{}:</b>\n".format(html.escape(chat.title)) + log_message

        return log_message

    else:
        message.reply_text("This user is not a Dragon Disaster!")
        return ""


@run_async
@sudo_plus
@gloggable
def removesupport(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in SUPPORT_USERS:
        message.reply_text("Requested HA to demote this user to Civilian")
        SUPPORT_USERS.remove(user_id)
        data['supports'].remove(user_id)

        with open(ELEVATED_USERS_FILE, 'w') as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (f"#UNSUPPORT\n"
                       f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                       f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

        if chat.type != 'private':
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message

    else:
        message.reply_text("This user is not a Demon level Disaster!")
        return ""


@run_async
@sudo_plus
@gloggable
def removewhitelist(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in WHITELIST_USERS:
        message.reply_text("Demoting to normal user")
        WHITELIST_USERS.remove(user_id)
        data['whitelists'].remove(user_id)

        with open(ELEVATED_USERS_FILE, 'w') as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (f"#UNWHITELIST\n"
                       f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                       f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

        if chat.type != 'private':
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    else:
        message.reply_text("This user is not a Wolf Disaster!")
        return ""


@run_async
@sudo_plus
@gloggable
def removetiger(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, 'r') as infile:
        data = json.load(infile)

    if user_id in TIGER_USERS:
        message.reply_text("Demoting to normal user")
        TIGER_USERS.remove(user_id)
        data['tigers'].remove(user_id)

        with open(ELEVATED_USERS_FILE, 'w') as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (f"#UNTIGER\n"
                       f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                       f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

        if chat.type != 'private':
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    else:
        message.reply_text("This user is not a Tiger Disaster!")
        return ""


@run_async
@whitelist_plus
def whitelistlist(bot: Bot, update: Update):
    reply = "<b>Known explorer Disasters 🔥:</b>\n"
    for each_user in WHITELIST_USERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)

            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def tigerlist(bot: Bot, update: Update):
    reply = "<b>Known knights Disasters 🔥:</b>\n"
    for each_user in TIGER_USERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def supportlist(bot: Bot, update: Update):
    reply = "<b>Known amateur Disasters 🔥:</b>\n"
    for each_user in SUPPORT_USERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def sudolist(bot: Bot, update: Update):
    true_sudo = list(set(SUDO_USERS) - set(DEV_USERS))
    reply = "<b>Known wielder Disasters 🔥:</b>\n"
    for each_user in true_sudo:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
@whitelist_plus
def devlist(bot: Bot, update: Update):
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply = "<b> List Of My Masters🔥:</b>\n"
    for each_user in true_dev:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


__help__ = """
 - /masters - Lists Of all Masters.
 - /wielder - Lists Of all wielder.
 - /amateur - Lists Of all amateur.
 - /knights - Lists Of all knights.
 - /explorer - Lists Of all explorer.
"""

SUDO_HANDLER = CommandHandler(("addsudo", "addwielder"), addsudo, pass_args=True)
SUPPORT_HANDLER = CommandHandler(("addsupport", "addamateur"), addsupport, pass_args=True)
TIGER_HANDLER = CommandHandler(("addknights"), addtiger, pass_args=True)
WHITELIST_HANDLER = CommandHandler(("addwhitelist", "addexplorer"), addwhitelist, pass_args=True)
UNSUDO_HANDLER = CommandHandler(("removesudo", "removewielder"), removesudo, pass_args=True)
UNSUPPORT_HANDLER = CommandHandler(("removesupport", "removeamateur"), removesupport, pass_args=True)
UNTIGER_HANDLER = CommandHandler(("removeknights"), removetiger, pass_args=True)
UNWHITELIST_HANDLER = CommandHandler(("removewhitelist", "removeexplorer"), removewhitelist, pass_args=True)

WHITELISTLIST_HANDLER = CommandHandler(["whitelistlist", "explorer"], whitelistlist)
TIGERLIST_HANDLER = CommandHandler(["knights"], tigerlist)
SUPPORTLIST_HANDLER = CommandHandler(["supportlist", "amateur"], supportlist)
SUDOLIST_HANDLER = CommandHandler(["sudolist", "wielder"], sudolist)
DEVLIST_HANDLER = CommandHandler(["devlist", "masters"], devlist)

dispatcher.add_handler(SUDO_HANDLER)
dispatcher.add_handler(SUPPORT_HANDLER)
dispatcher.add_handler(TIGER_HANDLER)
dispatcher.add_handler(WHITELIST_HANDLER)
dispatcher.add_handler(UNSUDO_HANDLER)
dispatcher.add_handler(UNSUPPORT_HANDLER)
dispatcher.add_handler(UNTIGER_HANDLER)
dispatcher.add_handler(UNWHITELIST_HANDLER)

dispatcher.add_handler(WHITELISTLIST_HANDLER)
dispatcher.add_handler(TIGERLIST_HANDLER)
dispatcher.add_handler(SUPPORTLIST_HANDLER)
dispatcher.add_handler(SUDOLIST_HANDLER)
dispatcher.add_handler(DEVLIST_HANDLER)

__mod_name__ = "DISASTERS"
__handlers__ = [SUDO_HANDLER, SUPPORT_HANDLER, TIGER_HANDLER, WHITELIST_HANDLER, 
                UNSUDO_HANDLER, UNSUPPORT_HANDLER, UNTIGER_HANDLER, UNWHITELIST_HANDLER,
                WHITELISTLIST_HANDLER, TIGERLIST_HANDLER, SUPPORTLIST_HANDLER,
                SUDOLIST_HANDLER, DEVLIST_HANDLER]
