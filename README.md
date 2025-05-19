# Step-by-Step Guide to Deploy the Telegram Bot for Monitoring Geth and Prysm

1️⃣ Step 1: Install Dependencies
SSH into your server and run the following commands to install necessary dependencies:

```shell
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv -y
pip3 install python-telegram-bot psutil
```

2️⃣ Step 2: Get Your Telegram Bot Token
Open Telegram and search for @BotFather.

Type /start and then /newbot.

Choose a name for your bot.

Choose a username (must end with bot).

You will receive a token like this:


Set the Telegram bot token in the environment:

```shell
export TELEGRAM_BOT_TOKEN='your_telegram_bot_token'
```


3️⃣ Step 3: Create the Python Script
Navigate to your home directory:




Create the script:

```shell
nano bot.py
```

Paste the Python script I provided in the previous message.

```shell
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

```



Replace the line with os.getenv("TELEGRAM_BOT_TOKEN"):


```shell
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
Replace YOUR_TELEGRAM_BOT_TOKEN with your actual bot token.
```

Save the file: CTRL + O, Enter, and CTRL + X.

4️⃣ Step 4: Run the Bot
You can run the bot with:

```shell
python3 bot.py
``` 
If you want it to run in the background, use:

```shell
nohup python3 bot.py &

To verify it is running:


5️⃣ Step 5: Test the Bot
Open your Telegram app.

Search for your bot using its name.

Type /status.

You should see buttons with options:

Check if Nodes Are Synced

Monitor Hardware Usage

Monitor Disk Usage

Geth Disk Usage

Prysm Disk Usage

Prune Geth Data

RPC Endpoints

RAM Usage

6️⃣ Step 6: Enable Auto-Start (Optional)
If you want the bot to auto-start after a reboot, create a systemd service:

bash
Copy code
sudo nano /etc/systemd/system/geth_prysm_bot.service
Paste the following configuration:

ini
Copy code
[Unit]
Description=Geth and Prysm Monitor Bot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/ubuntu/geth_prysm_bot/bot.py
WorkingDirectory=/home/ubuntu/geth_prysm_bot
StandardOutput=inherit
StandardError=inherit
Restart=always
User=ubuntu

[Install]
WantedBy=multi-user.target
Save and close (CTRL + O, Enter, CTRL + X).

Enable the service:

bash
Copy code
sudo systemctl enable geth_prysm_bot
sudo systemctl start geth_prysm_bot
Check the status:

bash
Copy code
sudo systemctl status geth_prysm_bot
7️⃣ Step 7: Firewall Rules (if needed)
If you have UFW enabled, make sure port 8545 and 3500 are allowed for local monitoring:

bash
Copy code
sudo ufw allow 8545
sudo ufw allow 3500
8️⃣ Step 8: Monitoring Commands
Here are the commands triggered by each button:

Check if Nodes Are Synced - Executes RPC calls to check if Geth and Prysm are fully synced.

Monitor Hardware Usage - Uses psutil to fetch CPU and RAM usage.

Monitor Disk Usage - Displays total and used disk space.

Geth Disk Usage - Shows disk usage for /root/ethereum/execution.

Prysm Disk Usage - Shows disk usage for /root/ethereum/consensus.

Prune Geth Data - Stops Geth, prunes historical data, and restarts it.

RPC Endpoints - Prints your Geth and Prysm RPC URLs.

RAM Usage - Detailed RAM information.

9️⃣ Optional: Logs Monitoring
To monitor the bot logs:

bash
Copy code
journalctl -u geth_prysm_bot -f
💡 Next Steps
Do you want me to extend this bot to:

Monitor live logs from Docker containers?

Alert you on Telegram if the sync falls behind a certain threshold?

Schedule automatic pruning every few months?

Would you like me to extend it with these capabilities?
