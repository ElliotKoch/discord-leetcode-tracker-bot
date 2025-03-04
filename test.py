import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os 

# Keys are stored locally in the '.env' file for security reasons.
load_dotenv()
github_data = json.load(open("data.json"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# Get recent commits (last 24 hours)
def get_recent_commits(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching commits: {response.status_code}")
        return []

    commits = response.json()
    one_day_ago = datetime.now() - timedelta(days=1)
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


for user in github_data["users"]:
    print(f"Fetching commits for user: {user['username']}")
    for repo in user["repos"]:  
        # Process commits
        print(user['username'],repo)
        recent_commits = get_recent_commits(user['username'], repo["name"])
        # Display results
        for folder, message in recent_commits:
            print(f"Folders: {folder}")
            print(f"Message: {message}")
            print("-" * 40)