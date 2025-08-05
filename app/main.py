import logging
import os
import csv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SOURCE_CHANNEL_ID_STR = os.environ.get("SOURCE_CHANNEL_ID")
GROUP_IDS_FILE = 'group_ids.csv'

# --- Configuration Validation ---
if not BOT_TOKEN:
    logger.error("FATAL: BOT_TOKEN environment variable not set.")
    exit(1)

try:
    SOURCE_CHANNEL_ID = int(SOURCE_CHANNEL_ID_STR)
    logger.info(f"Source channel/group ID: {SOURCE_CHANNEL_ID}")
except (ValueError, TypeError):
    logger.error(f"FATAL: SOURCE_CHANNEL_ID is not set or is not a valid integer: {SOURCE_CHANNEL_ID_STR}")
    exit(1)

# --- CSV Data Handling ---
def load_groups() -> dict[int, str]:
    """Loads group data from the CSV file into a dictionary."""
    groups = {}
    try:
        with open(GROUP_IDS_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    group_id = int(row['group_id'])
                    groups[group_id] = row['group_name']
                except (ValueError, KeyError, TypeError) as e:
                    logger.warning(f"Skipping invalid row in {GROUP_IDS_FILE}: {row}. Error: {e}")
    except FileNotFoundError:
        logger.info(f"{GROUP_IDS_FILE} not found. Starting with an empty list. It will be created on first add.")
    return groups

def save_groups(groups: dict[int, str]) -> None:
    """Saves group data to the CSV file."""
    with open(GROUP_IDS_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['group_id', 'group_name'])
        for group_id, group_name in sorted(groups.items()):
            writer.writerow([group_id, group_name])

# --- Command Handlers ---
async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Adds a new group to the list. Usage: /add <group_id> <group_name>"""
    if update.message.chat_id != SOURCE_CHANNEL_ID:
        logger.warning(f"Unauthorized /add attempt from chat_id: {update.message.chat_id}")
        return

    if len(context.args) < 2:
        await update.message.reply_text("<b>Usage:</b> /add &lt;group_id&gt; &lt;group_name&gt;\n<b>Example:</b> /add -100123456789 My Awesome Group", parse_mode='HTML')
        return

    try:
        group_id = int(context.args[0])
        group_name = " ".join(context.args[1:])
        
        groups = load_groups()
        if group_id in groups:
            await update.message.reply_text(f"Group ID {group_id} already exists with name: {groups[group_id]}.")
        else:
            groups[group_id] = group_name
            save_groups(groups)
            await update.message.reply_text(f"✅ Group '<b>{group_name}</b>' ({group_id}) added successfully.", parse_mode='HTML')
            logger.info(f"Group {group_id} ({group_name}) added.")
    except ValueError:
        await update.message.reply_text("Invalid Group ID. It must be a number.")

async def remove_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Removes a group from the list. Usage: /remove <group_id>"""
    if update.message.chat_id != SOURCE_CHANNEL_ID:
        logger.warning(f"Unauthorized /remove attempt from chat_id: {update.message.chat_id}")
        return

    if not context.args:
        await update.message.reply_text("<b>Usage:</b> /remove &lt;group_id&gt;", parse_mode='HTML')
        return

    try:
        group_id_to_remove = int(context.args[0])
        groups = load_groups()
        if group_id_to_remove in groups:
            removed_group_name = groups.pop(group_id_to_remove)
            save_groups(groups)
            await update.message.reply_text(f"🗑️ Group '<b>{removed_group_name}</b>' ({group_id_to_remove}) removed successfully.", parse_mode='HTML')
            logger.info(f"Group {group_id_to_remove} ({removed_group_name}) removed.")
        else:
            await update.message.reply_text(f"Group ID {group_id_to_remove} not found in the list.")
    except ValueError:
        await update.message.reply_text("Invalid Group ID. It must be a number.")

async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lists all saved groups."""
    if update.message.chat_id != SOURCE_CHANNEL_ID:
        logger.warning(f"Unauthorized /list attempt from chat_id: {update.message.chat_id}")
        return

    groups = load_groups()
    if not groups:
        await update.message.reply_text("No target groups have been added yet. Use /add to add one.")
        return

    message = "<b>Current Target Groups:</b>\n"
    message += "‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐\n"
    for group_id, group_name in sorted(groups.items()):
        message += f"<b>Name:</b> {group_name}\n<b>ID:</b> <code>{group_id}</code>\n‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐\n"
    
    await update.message.reply_text(message, parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays a help message with all available commands."""
    if update.message.chat_id != SOURCE_CHANNEL_ID:
        logger.warning(f"Unauthorized /help attempt from chat_id: {update.message.chat_id}")
        return

    help_text = """
<b>🤖 Bot Command Manual</b>

<b>--- Group Management ---</b>

/add &lt;group_id&gt; &lt;group_name&gt;
新增一個群組到推播列表中
範例: <code>/add -100123456 My_Group</code>

/remove &lt;group_id&gt;
將一個推播群組刪除
範例: <code>/remove -100123456</code>

/list
列出所有推播群組

<b>--- Message Forwarding ---</b>
(Must be a reply to a message)
先將要轉發的訊息輸入在群組中，然後 reply 這個訊息使用以下指令：

1.
/send &lt;group_name_1&gt;,&lt;group_name_2&gt;
轉送推播訊息到指定的群組中
範例: <code>/send My_Group_A,My_Group_B</code>

2.
/broadcast
轉送推播訊息到所有的群組

<b>--- General ---</b>

/help
顯示幫助訊息
"""
    await update.message.reply_text(help_text, parse_mode='HTML')


async def forward_message_to_targets(context: ContextTypes.DEFAULT_TYPE, from_chat_id: int, message_id: int, target_ids: list[int]):
    """Forwards a message to a list of target IDs."""
    for target_id in target_ids:
        try:
            await context.bot.copy_message(
                chat_id=target_id,
                from_chat_id=from_chat_id,
                message_id=message_id
            )
            logger.info(f"Successfully forwarded message to target {target_id}.")
        except Exception as e:
            logger.error(f"Failed to forward message to target {target_id}: {e}")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles forwarding commands from the source group."""
    message = update.message or update.channel_post
    if not message or message.chat_id != SOURCE_CHANNEL_ID:
        return

    if message.reply_to_message and message.text:
        command_text = message.text.strip()
        original_message_id = message.reply_to_message.message_id
        groups = load_groups()
        name_to_id_map = {name.lower(): gid for gid, name in groups.items()}

        if command_text.lower().startswith('/send'):
            arg_string = command_text[len('/send'):].strip()
            if not arg_string:
                await message.reply_text("<b>Usage:</b> Reply to a message with /send <group_name_1>,<group_name_2>,", parse_mode='HTML')
                return

            name_strings = arg_string.split(',')
            valid_targets = []
            invalid_entries = []

            for name_str in name_strings:
                clean_name = name_str.strip().lower()
                target_id = name_to_id_map.get(clean_name)
                if target_id:
                    valid_targets.append(target_id)
                else:
                    invalid_entries.append(f"<code>{name_str.strip()}</code> (not found)")

            if valid_targets:
                await forward_message_to_targets(context, SOURCE_CHANNEL_ID, original_message_id, valid_targets)
                sent_to_names = [f"<b>{groups[gid]}</b> (<code>{gid}</code>)" for gid in valid_targets]
                await message.reply_text(f"✅ Message sent to: {', '.join(sent_to_names)}.", parse_mode='HTML')

            if invalid_entries:
                await message.reply_text(f"⚠️ Could not send to the following: {', '.join(invalid_entries)}.", parse_mode='HTML')

        elif command_text.lower() == '/broadcast':
            if groups:
                await forward_message_to_targets(context, SOURCE_CHANNEL_ID, original_message_id, list(groups.keys()))
                await message.reply_text(f"Message broadcast to all <b>{len(groups)}</b> groups.", parse_mode='HTML')
            else:
                await message.reply_text("There are no target groups to broadcast to.")

def main() -> None:
    """Start the bot."""
    logger.info("Starting bot...")
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("add", add_group))
    application.add_handler(CommandHandler("remove", remove_group))
    application.add_handler(CommandHandler("list", list_groups))
    application.add_handler(CommandHandler("help", help_command))
    
    # Handler for forwarding commands (/send, /broadcast) which must be replies
    application.add_handler(MessageHandler(filters.REPLY & filters.COMMAND, message_handler))

    logger.info("Bot is running and polling for updates...")
    application.run_polling()


if __name__ == "__main__":
    main()
