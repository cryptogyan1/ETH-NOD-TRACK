import os
import subprocess
import psutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# Environment variable for bot token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Check if nodes are synced
def check_sync():
    try:
        geth_status = subprocess.check_output(
            "curl -X POST -H 'Content-Type: application/json' --data '{\"jsonrpc\":\"2.0\",\"method\":\"eth_syncing\",\"params\":[],\"id\":1}' http://localhost:8545",
            shell=True
        ).decode()
        
        prysm_status = subprocess.check_output(
            "curl http://localhost:3500/eth/v1/node/syncing", shell=True
        ).decode()

        return f"Geth Sync Status:\n{geth_status}\n\nPrysm Sync Status:\n{prysm_status}"
    except Exception as e:
        return f"Error checking sync: {e}"

# Get disk usage
def get_disk_usage(path):
    usage = psutil.disk_usage(path)
    return f"{usage.used // (1024**3)} GB / {usage.total // (1024**3)} GB"

# Check hardware usage
def check_hardware():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    return f"CPU Usage: {cpu}%\nRAM Usage: {ram.percent}% ({ram.used // (1024**3)} GB / {ram.total // (1024**3)} GB)"

# Prune Geth data
def prune_geth():
    try:
        prune_cmd = "docker compose down && docker volume rm ethereum_execution && docker compose up -d"
        subprocess.run(prune_cmd, shell=True)
        return "Geth historical data pruned and node restarted."
    except Exception as e:
        return f"Error pruning data: {e}"

# RPC endpoints
def get_rpc_endpoints():
    return "Geth RPC: http://localhost:8545\nPrysm RPC: http://localhost:3500"

# Generate the keyboard
def generate_keyboard():
    keyboard = [
        [InlineKeyboardButton("1. Check if Nodes Are Synced", callback_data="check_sync")],
        [InlineKeyboardButton("2. Monitor Hardware Usage", callback_data="hardware")],
        [InlineKeyboardButton("3. Monitor Disk Usage", callback_data="disk_usage")],
        [InlineKeyboardButton("4. Geth Disk Usage", callback_data="geth_disk")],
        [InlineKeyboardButton("5. Prysm Disk Usage", callback_data="prysm_disk")],
        [InlineKeyboardButton("6. Prune Geth Data", callback_data="prune")],
        [InlineKeyboardButton("7. RPC Endpoints", callback_data="rpc")],
        [InlineKeyboardButton("8. RAM Usage", callback_data="ram_usage")],
    ]
    return InlineKeyboardMarkup(keyboard)

# Command handler for /status
def status(update: Update, context):
    update.message.reply_text("Choose an option:", reply_markup=generate_keyboard())

# Callback handler for buttons
def button_handler(update: Update, context):
    query = update.callback_query
    query.answer()

    if query.data == "check_sync":
        response = check_sync()
    elif query.data == "hardware":
        response = check_hardware()
    elif query.data == "disk_usage":
        response = get_disk_usage("/")
    elif query.data == "geth_disk":
        response = get_disk_usage("/root/ethereum/execution")
    elif query.data == "prysm_disk":
        response = get_disk_usage("/root/ethereum/consensus")
    elif query.data == "prune":
        response = prune_geth()
    elif query.data == "rpc":
        response = get_rpc_endpoints()
    elif query.data == "ram_usage":
        ram = psutil.virtual_memory()
        response = f"RAM Usage: {ram.used // (1024**3)} GB / {ram.total // (1024**3)} GB"
    else:
        response = "Unknown option."

    query.edit_message_text(text=response)

# Main function to start the bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("status", status))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
