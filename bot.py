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
    # Get the commits for a repository
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    commits = response.json()
    # set the day deadline for commits
    days_ago = datetime.now() - timedelta(days=day)
    recent_commits = []

    # Keep only the commits that are before the days deadline 
    for commit in commits:
        # Extract the date
        commit_date = datetime.strptime(commit["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ")
        if commit_date > days_ago:
            sha = commit["sha"]
            message = commit["commit"]["message"]
            # Retrieve the folder of the commit
            folder_names = get_commit_folders(owner, repo, sha)
            # Filter with the Readme commits 
            if "readme" not in message.lower() and "Unknown" not in folder_names:
                recent_commits.append((folder_names[0], message))
    return recent_commits

# Get top-level folder(s) from a commit
def get_commit_folders(owner, repo, sha):
    # Get the information about the commit
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return ["Unknown"]

    commit_data = response.json()
    files = commit_data.get("files", [])

    # Extract top-level folder names
    folders = [file["filename"].split("/")[0] for file in files if "/" in file["filename"]]

    # Get unique folder names
    return list(set(folders)) if folders else ["Unknown"]


def add_to_database(username: str, repo: str):
    # Load the json database
    github_data = json.load(open("data.json"))
    # First check if the user already exists in the database
    for user in github_data["users"]:
        if username == user['username']:  
            # If it is the case, we do the same for the repository to be added
            for repository in user["repos"]:  
                if repo == repository["name"]:
                    return f"Repository {repo} is already in the database for {username}."
                else:
                    continue
            # In case the repository is not yet in the database, we check that it is a real repo for that user on Github
            url = f"https://api.github.com/repos/{username}/{repo}"
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return f"There exists no repository named {repo} in Github for user {username}."
            else:
                # Add new repo to existing user
                user["repos"].append({"name": repo})
                # Save back the database
                with open("./data.json", "w", encoding="utf-8") as f:
                    json.dump(github_data, f, indent=4)
                return "Repository added to existing user."
    # In case it's a new user, we check if the user exists on Github        
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"There exists no {username} in Github."
    else:
        # If the user exists, we check for the repository
        url = f"https://api.github.com/repos/{username}/{repo}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
                return f"There exists no repository named {repo} in Github for user {username}."
        else:
            # Add new user with repo
            github_data["users"].append({"username": username, "repos": [{"name": repo}]})
            # Save back the database
            with open("./data.json", "w", encoding="utf-8") as f:
                json.dump(github_data, f, indent=4)
            return "New user and repository added."

def delete_from_database(username,repo):
    # Load the json database
    github_data = json.load(open("data.json"))
    # Check that a repository is given as argument
    if repo:
        # if it's the case, we go in the repo dictionary for the corresponding user
        for user in github_data["users"]:
            if username == user['username']: 
                # Filter the list of repo (dictionary) to keep those that do not match to the given repo name  
                user['repos'] = [repository for repository in user["repos"] if repository["name"] != repo]
                # Save back the database
                with open("./data.json", "w", encoding="utf-8") as f:
                    json.dump(github_data, f, indent=4)
                return f"Repository {repo} was removed from the database for {username}, if it exits."   
            else:
                continue
        return f"There exists no user {username} in the database."
    else:
        # If no repo is given, we filter the list of user dictionary to keep those that do not match the given username  
        github_data["users"] = [user for user in github_data["users"] if user["username"] != username]
        # Save back the database
        with open("./data.json", "w", encoding="utf-8") as f:
            json.dump(github_data, f, indent=4)
        return f"User {username} was removed from the database, if it exists."

def show_database():
    # Load JSON data from file
    github_data = json.load(open("data.json", encoding="utf-8"))

    # Convert to a single string in a readable format
    github_data_string = "".join(
        f"**User:** *{user['username']}* | **Repos:** *{', '.join(repo['name'] for repo in user['repos'])}*" + "\n"
        for user in github_data["users"]
    )
    return github_data_string


# Create an instance of a bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/',intents=intents)

@bot.command(description="Add a GitHub user and/or repository (leetcode) to the database.")  
async def add(ctx,  
    username: str = commands.parameter(description="GitHub username to add or the user to whom the repository should be assigned."),  
    repo: str = commands.parameter(description="Name of the GitHub repository to associate with the specified user.")):  
    await ctx.send(add_to_database(username, repo))

@bot.command(description="Show the database")
async def database(ctx):
    await ctx.send(show_database())


@bot.command(description="Remove a GitHub user or a specific repository from the database.")  
async def delete(ctx,  
    username: str = commands.parameter(description="GitHub username to remove or the user whose repository should be deleted."),  
    repo: str = commands.parameter(default=None, description="Optional. Name of the repository to delete. If omitted, the entire user will be removed.")):  
    await ctx.send(delete_from_database(username, repo))

@bot.command(description="Retrieve solved LeetCode problems within a specified number of days.")  
async def resume(ctx, days: int = commands.parameter(description="Fetch problems solved in the last X days.")):  
    if days>0:
        # Loading Json data
        github_data = json.load(open("data.json"))
        output = ""
        for user in github_data["users"]:
            output += f"**{user['username']}:**"
            for repo in user["repos"]:  
                # Process commits
                recent_commits = get_recent_commits(user['username'], repo["name"],days)
                # Display results
                for folder, message in recent_commits:
                    output += f"\n- ***{folder}***: *{message}*"
                output += '\n' + f"-" * 100 + '\n'
        await ctx.send(output)
    else:
        await ctx.send(f"**The number of day(s) must be a positive integer!**")

# Creates a handler for the logs
handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
bot.run(BOT_TOKEN, log_handler=handler, log_level=logging.DEBUG)