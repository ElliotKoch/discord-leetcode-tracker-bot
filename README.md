
# Discord LeetCode Tracker Bot

## 📌 Project Overview
This project is a Discord bot designed to track LeetCode problem-solving activity via GitHub repositories. The bot allows users to:
- Add or remove LeetCode-related users and repositories to/from a local database.
- Retrieve recent commits from LeetCode repositories.
- Filter commits from the last few days to track progress.
- Organize repositories by folder names and commit messages.

The bot interacts with the GitHub API to fetch commit data and organize LeetCode problem-solving activity for users.

## 📂 Repository Structure
```
LeetCode-Repository-Tracker-Bot/
│── bot.py                                      # Main bot script
│── data.json                                   # Database containing GitHub users and repositories
│── .env                                        # Environment file for sensitive data like bot token and GitHub API token
│── README.md                                   # Project documentation
│── requirements.txt                            # Required dependencies
```

## ⚙️ Installation & Setup
To run the project, follow these steps with Python version 3.11.9:

1. **Clone the repository**
   ```sh
   git clone https://github.com/ElliotKoch/discord-leetcode-tracker-bot.git
   cd discord-leetcode-tracker-bot
   ```
   
2. **Setup virtual environment**
   ```sh
   python -m venv .venv
   .venv\Scripts\activate   # For Windows
   source .venv/bin/activate   # For Linux/Mac
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Create a `.env` file in the root directory of the project.
   - Add the following content:
     ```
     BOT_TOKEN=your_discord_bot_token
     GITHUB_TOKEN=your_github_api_token
     ```

5. **Run the bot**
   ```sh
   python bot.py
   ```

6. **Close the virtual environment**
   ```sh
   deactivate
   ```

## 📊 Features
- **Add Users and Repositories**: Add LeetCode-related GitHub users and repositories to the database.
- **Remove Users and Repositories**: Remove users or repositories from the database.
- **Fetch Recent Commits**: Retrieve commits from the past X days for LeetCode repositories.
- **Show Database**: Display all users and repositories in the database.

## 🚀 Usage
Once the bot is running on Discord, you can use the following commands:
- `/add <username> <repo>`: Adds a GitHub user and repository (LeetCode-related) to the database.
- `/delete <username> <repo>`: Removes a user or repository from the database.
- `/database`: Displays all users and repositories in the database.
- `/resume <days>`: Retrieves commits from the past specified number of days, focusing on LeetCode problems solved.

## 📜 License
This project is open-source and free to use for educational or personal purposes, especially for tracking LeetCode progress.

## 📧 Contact
For any inquiries, contact me (**Elliot Koch**) at [kochelliotpro@gmail.com].
