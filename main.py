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

def remove_last_line_from_file(filepath: Path) -> bool:
    """Remove the last non-empty line from a file"""
    if not filepath.exists():
        return False
    
    with open(filepath, "r") as f:
        lines = [line for line in f if line.strip()]
    
    if not lines:
        return False
    
    lines = lines[:-1]
    
    with open(filepath, "w") as f:
        f.writelines(lines)
    
    return True

def get_last_drink_info(username: str) -> tuple:
    """Get the last drink type and timestamp"""
    user_dir = Path(f"data/{username}")
    if not user_dir.exists():
        return None, None
    
    tea_file = user_dir / "tea.txt"
    coffee_file = user_dir / "coffee.txt"
    
    last_tea_time = None
    last_coffee_time = None
    
    if tea_file.exists():
        with open(tea_file, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                last_tea_time = datetime.fromisoformat(lines[-1].replace('Z', '+00:00'))
    
    if coffee_file.exists():
        with open(coffee_file, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                last_coffee_time = datetime.fromisoformat(lines[-1].replace('Z', '+00:00'))
    
    if last_tea_time and last_coffee_time:
        if last_tea_time > last_coffee_time:
            return "tea", last_tea_time
        else:
            return "coffee", last_coffee_time
    elif last_tea_time:
        return "tea", last_tea_time
    elif last_coffee_time:
        return "coffee", last_coffee_time
    else:
        return None, None

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

@app.get("/stats_all")
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

@app.post("/{username}/undo")
def undo_last_drink(username: str):
    init_user(username)
    
    drink_type, last_time = get_last_drink_info(username)
    
    if not drink_type or not last_time:
        return {
            "user": username,
            "message": "No drinks to undo",
            "success": False
        }
    
    now = datetime.now(UTC)
    time_diff = now - last_time
    
    if time_diff.total_seconds() > 60:
        return {
            "user": username,
            "message": "Cannot undo - last drink was more than 1 minute ago",
            "success": False
        }
    
    user_dir = Path(f"data/{username}")
    file_path = user_dir / f"{drink_type}.txt"
    
    success = remove_last_line_from_file(file_path)
    
    if success:
        git_success = git_commit_and_push(username, f"undo {drink_type}")
        return {
            "user": username,
            "message": f"Successfully undid last {drink_type}",
            "success": True,
            "git_push": "success" if git_success else "failed"
        }
    else:
        return {
            "user": username,
            "message": "Failed to undo",
            "success": False
        }