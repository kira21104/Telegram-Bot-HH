# Telegram Bot Vacancy Search

This project is a Telegram bot built with Python that allows users to search for job vacancies in specific regions, experience levels, and categories on the hh.ru job search platform. The bot fetches and sends job vacancy links in response to user selections.

## Features

- **Interactive interface**: Users can select a region (Moscow or St. Petersburg), an experience level (Junior, Middle, Senior), and a job category (Data Analyst, Data Scientist, Data Engineer).
- **Job Search**: The bot scrapes vacancy data from hh.ru based on the selected filters and provides links to the job listings.
- **Easy to Use**: A simple, user-friendly Telegram bot interface.

## Installation

### Requirements

- Python 3.7+
- Telegram Bot API Token
- Dependencies:
  - `requests`
  - `beautifulsoup4`
  - `fake_useragent`
  - `pyTelegramBotAPI` (Telebot)

You can install the required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

## Bot setup

1. Create a new Telegram bot by talking to BotFather on Telegram.
2. Get a bot API token from BotFather.
3. Replace the TOKEN variable in your code with your bot's token

## Usage

### Running a bot
After setting up the bot and installing dependencies, run the Python script:
python bot.py
Once the bot is launched, you can interact with it via Telegram. The bot will guide you through the process of selecting your region, experience level, and job category.

### Teams
/start : Starts the bot and shows the main menu with region selection.

### Interaction flow
1. Region selection: select “Moscow” or “St. Petersburg”.
2. Experience Level: Select Junior, Intermediate, or Senior.
3. Select Category: Select a job category, such as Data Analyst, Data Scientist, or Data Engineer.
4. Job Listings: The bot will display job links based on your selections.

### Example Workflow
1. The user starts the bot using /start.
2. The bot asks the user to select a region.
3. The user selects a region and the bot asks for an experience level.
4. After selecting your experience level, the bot prompts you for the job category.
5. The bot scans hh.ru and sends links to relevant job postings.
