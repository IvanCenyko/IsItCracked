# IsItCracked

Telegram bot, made with python and the [Telebot](https://github.com/eternnoir/pyTelegramBotAPI) library. It notifies its users daily about the crack status of the games they've chosen.

[![bot](https://img.shields.io/badge/chat%20with%20the%20bot-1DA1F2?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/is_it_cracked_bot)




## Commands
- /add <game> - adds a game to the user's list.
- /remove - allows to remove a game from the user's list.
- /status - shows the real time status of the games on the user's list.



## Run Locally

### Clone the project

```bash
  git clone https://github.com/IvanCenyko/IsItCracked.git
```

### Go to the project directory

```bash
  cd IsItCracked
```

### Install dependencies

```bash
  pip install -r requirements.txt
```

### Create a .env file with your Telegram bot token

- #### Linux
  ```bash
    touch .env
  ```

### Edit the file

- #### Linux
  ```bash
    nano .env
  ```

### Put your token this way and save the file

```env
  TOKEN = your_token_here
```

### Start the bot

```bash
  python bot.py
```


