import logging
import os
import subprocess
from fastapi import FastAPI
from datetime import datetime, UTC
from pathlib import Path
from dotenv import load_dotenv
import threading

lock = threading.Lock()


load_dotenv()
app = FastAPI(title="Tea counter")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def home():
    return {"message": "this is the tea/coffee counter"}

def init_user(username: str):
    user_dir = Path(f"./data/{username}")
    user_dir.mkdir(exist_ok=True, parents=True)

    tea_file = user_dir / "tea.txt"
    coffee_file = user_dir / "coffee.txt"

    if not tea_file.exists():
        tea_file.touch()
    if not coffee_file.exists():
        coffee_file.touch()

def append_timestamp_to_file(filepath: Path):
    timestamp = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(filepath, "a") as f:
        f.write(f"{timestamp}\n")

def increment_coffee(username: str):
    append_timestamp_to_file(filepath=Path(f"data/{username}/coffee.txt"))

def increment_tea(username: str):
    append_timestamp_to_file(filepath=Path(f"data/{username}/tea.txt"))

def count_lines_in_file(filepath: Path) -> int:
    if not filepath.exists():
        return 0
    
    with open(filepath, "r") as f:
        return len([line for line in f if line.strip()])

def git_commit_and_push(username: str, drink_type: str):
    """Commit changes and push to GitHub"""
    try:
        with lock:
            # Add all changes in data directory
            result = subprocess.run(["git", "add", f"data/{username}/"], cwd=Path.cwd(), capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to add files for {username}'s {drink_type}: {result.stderr}")
                return False
            
            # Create commit message
            commit_message = f"{username} registered {drink_type} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Commit changes
            result = subprocess.run(["git", "commit", "-m", commit_message], cwd=Path.cwd(), capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to commit {username}'s {drink_type}: {result.stderr}")
                return False
            
            # Push to GitHub
            result = subprocess.run(["git", "push", "origin", "main"], cwd=Path.cwd(), capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to push {username}'s {drink_type}: {result.stderr}")
                return False
                
            logger.info(f"Successfully pushed {username}'s {drink_type} to GitHub")
            return True
        
    except Exception as e:
        logger.error(f"Unexpected error in git operations: {str(e)}")
        return False
    
@app.post("/{username}/coffee")
def register_coffee(username: str):
    init_user(username)
    increment_coffee(username)
    git_success = git_commit_and_push(username, "coffee")

    return {
        "user": username,
        "message": "coffee registered!",
        "git_push": "success"  if git_success else "failed"
    }

@app.post("/{username}/tea")
def register_tea(username: str):
    init_user(username)
    increment_tea(username)
    git_success = git_commit_and_push(username, "tea")

    return {
        "user": username,
        "message": "tea registered!",
        "git_push": "success"  if git_success else "failed"
    }

@app.get("/stats/{username}")
def get_user_stats(username: str):
    user_dir = Path(f"data/{username}")

    if not user_dir.exists():
        return {
            "user": username,
            "tea": 0,
            "coffee": 0,
        }
    
    tea_count = count_lines_in_file(user_dir / "tea.txt")
    coffee_count = count_lines_in_file(user_dir / "coffee.txt")

    return {
        "user": username,
        "tea": tea_count,
        "coffee": coffee_count,
    }

@app.get("/stats/all")
def get_all_stats():
    all_data = {
        "tea": 0,
        "coffee": 0
    }

    for user in os.listdir("data"):
        user_data = get_user_stats(user)
        all_data["coffee"] += user_data["coffee"]
        all_data["tea"] += user_data["tea"]
    
    return all_data