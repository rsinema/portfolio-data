#!/usr/bin/env python3
"""
Portfolio Data Manager

A CLI tool to manage your portfolio data stored in GitHub.
"""

import argparse
import json
import os
import sys
import tempfile
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Configuration - Update these values
REPO_URL = "https://github.com/rsinema/portfolio-data.git"
JSON_PATH = "portfolio.json"
EDITOR = os.environ.get("EDITOR", "vim")  # Default to vim if no EDITOR is set


def load_portfolio(local_path: str) -> Dict[str, Any]:
    """Load the portfolio data from the local file."""
    try:
        with open(os.path.join(local_path, JSON_PATH), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find portfolio file at {JSON_PATH}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: {JSON_PATH} contains invalid JSON")
        sys.exit(1)


def save_portfolio(data: Dict[str, Any], local_path: str) -> None:
    """Save the portfolio data to the local file."""
    try:
        with open(os.path.join(local_path, JSON_PATH), "w") as f:
            json.dump(data, f, indent=2)
        print(f"Portfolio data saved successfully to {JSON_PATH}")
    except Exception as e:
        print(f"Error saving data: {e}")
        sys.exit(1)


def clone_or_pull_repo(repo_path: str) -> None:
    """Clone the repo if it doesn't exist, or pull updates if it does."""
    if not os.path.exists(repo_path):
        print(f"Cloning repository from {REPO_URL}...")
        subprocess.run(["git", "clone", REPO_URL, repo_path], check=True)
    else:
        print("Pulling latest changes...")
        subprocess.run(["git", "pull"], cwd=repo_path, check=True)


def commit_and_push(repo_path: str, commit_message: str) -> None:
    """Commit changes and push to the remote repository."""
    subprocess.run(["git", "add", JSON_PATH], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_path, check=True)
    subprocess.run(["git", "push"], cwd=repo_path, check=True)
    print("Changes committed and pushed to GitHub.")


def open_editor(file_path: str) -> None:
    """Open the specified file in the user's preferred editor."""
    try:
        subprocess.run([EDITOR, file_path], check=True)
    except subprocess.CalledProcessError:
        print(f"Error: Failed to open editor {EDITOR}")
        sys.exit(1)


def display_portfolio(data: Dict[str, Any]) -> None:
    """Display a summary of the portfolio data."""
    print("\n=== Portfolio Summary ===")
    print(f"Name: {data.get('name', 'N/A')}")
    print(f"Title: {data.get('title', 'N/A')}")
    
    print(f"\nSkills: {', '.join(data.get('skills', []))}")
    
    projects = data.get('projects', [])
    print(f"\nProjects ({len(projects)}):")
    for i, project in enumerate(projects, 1):
        print(f"  {i}. {project.get('title', 'Untitled Project')}")
    
    timeline = data.get('timeline', [])
    print(f"\nTimeline Entries ({len(timeline)}):")
    for i, entry in enumerate(timeline, 1):
        print(f"  {i}. {entry.get('title', 'Untitled Entry')} ({entry.get('type', 'unknown')})")
    print("\n")


def edit_portfolio(data: Dict[str, Any]) -> Dict[str, Any]:
    """Edit the entire portfolio JSON in the user's preferred editor."""
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w+", delete=False) as temp:
        json.dump(data, temp, indent=2)
        temp_path = temp.name
    
    open_editor(temp_path)
    
    try:
        with open(temp_path, "r") as f:
            updated_data = json.load(f)
        os.unlink(temp_path)
        return updated_data
    except json.JSONDecodeError:
        print("Error: The edited file contains invalid JSON. Changes not saved.")
        choice = input("Would you like to try editing again? (y/n): ").lower()
        if choice == 'y':
            return edit_portfolio(data)
        else:
            os.unlink(temp_path)
            return data


def add_project(data: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new project to the portfolio."""
    projects = data.get('projects', [])
    
    new_project = {
        "title": input("Project title: "),
        "description": input("Project description: "),
        "links": [],
        "skills": []
    }
    
    # Add links
    while True:
        link_text = input("Link text (or press Enter to skip): ")
        if not link_text:
            break
        link_url = input("Link URL: ")
        new_project["links"].append({"text": link_text, "url": link_url})
    
    # Add skills
    print("Enter skills (one per line, press Enter on a blank line to finish):")
    while True:
        skill = input("> ")
        if not skill:
            break
        new_project["skills"].append(skill)
    
    projects.append(new_project)
    data['projects'] = projects
    print(f"Added new project: {new_project['title']}")
    return data

def delete_project(data: Dict[str, Any]) -> Dict[str, Any]:
    """Delete a project from the portfolio."""
    projects = data.get('projects', [])
    project_title = input("Enter the title of the project you would like to delete: ")
    
    for project in projects:
        if project['title'] == project_title:
            projects.remove(project)
            print(f"Deleted project: {project_title}")
            break
    else:
        print(f"Project '{project_title}' not found.")
    
    data['projects'] = projects
    return data


def add_timeline_entry(data: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new timeline entry to the portfolio."""
    timeline = data.get('timeline', [])
    
    entry_type = ""
    while entry_type not in ['education', 'work']:
        entry_type = input("Entry type (education/work): ").lower()
    
    new_entry = {
        "title": input("Title: "),
        "organization": input("Organization: "),
        "location": input("Location: "),
        "startDate": input("Start date: "),
        "endDate": input("End date (or 'Present'): "),
        "type": entry_type,
        "description": [],
        "technologies": []
    }
    
    # Add description points
    print("Enter description points (one per line, press Enter on a blank line to finish):")
    while True:
        desc = input("> ")
        if not desc:
            break
        new_entry["description"].append(desc)
    
    # Add technologies
    print("Enter technologies (one per line, press Enter on a blank line to finish):")
    while True:
        tech = input("> ")
        if not tech:
            break
        new_entry["technologies"].append(tech)
    
    timeline.append(new_entry)
    data['timeline'] = timeline
    print(f"Added new timeline entry: {new_entry['title']}")
    return data


def add_skill(data: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new skill to the portfolio."""
    skills = data.get('skills', [])
    new_skill = input("Enter new skill: ")
    
    if new_skill and new_skill not in skills:
        skills.append(new_skill)
        data['skills'] = skills
        print(f"Added new skill: {new_skill}")
    elif new_skill in skills:
        print(f"Skill '{new_skill}' already exists.")
    
    return data


def main():
    parser = argparse.ArgumentParser(description="Manage your portfolio data")
    parser.add_argument("--repo-dir", help="Local directory for the repository", default="/Users/rileysinema/Documents/portfolio-data")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Pull command
    subparsers.add_parser("pull", help="Pull latest changes from GitHub")
    
    # View command
    subparsers.add_parser("view", help="View portfolio summary")
    
    # Edit command
    edit_parser = subparsers.add_parser("edit", help="Edit portfolio data")
    edit_parser.add_argument("--message", "-m", help="Commit message", default=f"Update portfolio data - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Add project command
    add_project_parser = subparsers.add_parser("add-project", help="Add a new project")
    add_project_parser.add_argument("--message", "-m", help="Commit message", default=f"Add new project - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Delete project command
    delete_project_parser = subparsers.add_parser("delete-project", help="Delete a project")
    delete_project_parser.add_argument("--message", "-m", help="Commit message", default=f"Delete project - {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Add timeline entry command
    add_timeline_parser = subparsers.add_parser("add-timeline", help="Add a new timeline entry")
    add_timeline_parser.add_argument("--message", "-m", help="Commit message", default=f"Add new timeline entry - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Add skill command
    add_skill_parser = subparsers.add_parser("add-skill", help="Add a new skill")
    add_skill_parser.add_argument("--message", "-m", help="Commit message", default=f"Add new skill - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    args = parser.parse_args()
    
    # Create or update the local repo
    repo_path = os.path.abspath(args.repo_dir)
    try:
        clone_or_pull_repo(repo_path)
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        sys.exit(1)
    
    if args.command == "pull":
        print("Repository updated successfully.")
        sys.exit(0)
    
    # Load the data
    portfolio_data = load_portfolio(repo_path)
    
    if args.command == "view":
        display_portfolio(portfolio_data)
    
    elif args.command == "edit":
        updated_data = edit_portfolio(portfolio_data)
        save_portfolio(updated_data, repo_path)
        commit_and_push(repo_path, args.message)
    
    elif args.command == "add-project":
        updated_data = add_project(portfolio_data)
        save_portfolio(updated_data, repo_path)
        commit_and_push(repo_path, args.message)

    elif args.command == "delete-project":
        updated_data = delete_project(portfolio_data)
        save_portfolio(updated_data, repo_path)
        commit_and_push(repo_path, args.message)
    
    elif args.command == "add-timeline":
        updated_data = add_timeline_entry(portfolio_data)
        save_portfolio(updated_data, repo_path)
        commit_and_push(repo_path, args.message)
    
    elif args.command == "add-skill":
        updated_data = add_skill(portfolio_data)
        save_portfolio(updated_data, repo_path)
        commit_and_push(repo_path, args.message)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()