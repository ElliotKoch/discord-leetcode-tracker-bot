from discord.ext import commands
from datetime import datetime, timedelta
from dotenv import load_dotenv
import discord
import json
import requests
import os
import logging


# Keys are stored locally in the '.env' file for security reasons.
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# Function to get commits from past days
def get_recent_commits(owner, repo, day):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching commits: {response.status_code}")
        return []

    commits = response.json()
    one_day_ago = datetime.now() - timedelta(days=day)
    recent_commits = []

    for commit in commits:
        commit_date = datetime.strptime(commit["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ")
        if commit_date > one_day_ago:
            sha = commit["sha"]
            message = commit["commit"]["message"]
            folder_names = get_commit_folders(owner, repo, sha)
            # Apply the filtering conditions
            if "readme" not in message.lower() and "Unknown" not in folder_names:
                recent_commits.append((folder_names[0], message))

    return recent_commits

# Get top-level folder(s) from a commit
def get_commit_folders(owner, repo, sha):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching commit details for {sha}: {response.status_code}")
        return ["Unknown"]

    commit_data = response.json()
    files = commit_data.get("files", [])

    # Extract top-level folder names
    folders = [file["filename"].split("/")[0] for file in files if "/" in file["filename"]]

    # Get unique folder names
    return list(set(folders)) if folders else ["Unknown"]


def add_to_database(username: str, repo: str):
    github_data = json.load(open("data.json"))
    for user in github_data["users"]:
        if username == user['username']:  
            for repository in user["repos"]:  
                if repo == repository["name"]:
                    return f"Repository {repo} is already in the database for {username}."
                else:
                    continue
            url = f"https://api.github.com/repos/{username}/{repo}"
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return f"There exists no repository named {repo} in Github for user {username}."
            else:
                # Add new repo to existing user
                user["repos"].append({"name": repo})
                with open("./data.json", "w", encoding="utf-8") as f:
                    json.dump(github_data, f, indent=4)
                
                print("Repository added to existing user.")
                return "Repository added to existing user."
            
    url = f"https://api.github.com/repos/{username}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(response.status_code)
        return f"There exists no {username} in Github."
    else:
        url = f"https://api.github.com/repos/{username}/{repo}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
                return f"There exists no repository named {repo} in Github for user {username}."
        else:
            # If user doesn't exist, add new user with repo
            github_data["users"].append({"username": username, "repos": [{"name": repo}]})
            with open("./data.json", "w", encoding="utf-8") as f:
                json.dump(github_data, f, indent=4)
            return "New user and repository added."




# Create an instance of a bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/',intents=intents)

# Loading Json data
# github_data = json.load(open("data.json"))

@bot.command()
async def add(ctx, username: str, repo: str):
    await ctx.send(add_to_database(username,repo))

@bot.command()
async def resume(ctx, days: int):
    if days>0:
        # Loading Json data
        github_data = json.load(open("data.json"))
        output = ""
        for user in github_data["users"]:
            output += f"**{user['username']}:**"
            print(f"Fetching commits for user: {user['username']}")
            for repo in user["repos"]:  
                # Process commits
                print(user['username'],repo)
                recent_commits = get_recent_commits(user['username'], repo["name"],days)
                # Display results
                for folder, message in recent_commits:
                    output += f"\n- ***{folder}***: *{message}*"
                    print(f"Folders: {folder}")
                    print(f"Message: {message}")
                    print("-" * 40)
                output += '\n' + f"-" * 100 + '\n'
        await ctx.send(output)
    else:
        await ctx.send(f"**The number of day(s) must be a positive integer!**")

# Creates a handler for the logs
#handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
#client.run(BOT_TOKEN)#, log_handler=handler, log_level=logging.DEBUG)
bot.run(BOT_TOKEN)