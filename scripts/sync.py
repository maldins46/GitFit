import os
import sys
import subprocess
from datetime import datetime, timedelta, date

import requests
from github import Github, InputGitTreeElement
from stravalib import Client
from dateutil import parser as date_parser

COMMITS_PER_KM = 1
ACTIVITY_FILE = "activity.log"
COMMIT_MESSAGE = "GitFit sync"


def get_strava_access_token():
    client_id = os.environ.get("STRAVA_CLIENT_ID")
    client_secret = os.environ.get("STRAVA_CLIENT_SECRET")
    refresh_token = os.environ.get("STRAVA_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        print("ERROR: Missing Strava credentials")
        sys.exit(1)

    response = requests.post(
        "https://www.strava.com/api/v3/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    )

    if response.status_code != 200:
        print(f"ERROR: Failed to refresh token: {response.text}")
        sys.exit(1)

    return response.json()["access_token"]


def get_activities(access_token, target_date):
    client = Client(access_token)

    start_date = datetime.combine(target_date, datetime.min.time())
    end_date = datetime.combine(target_date, datetime.max.time())

    activities = list(
        client.get_activities(
            after=start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            before=end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            limit=100,
        )
    )

    return activities


def calculate_commits(activity):
    distance_km = (activity.distance or 0) / 1000.0

    commits = int(distance_km * COMMITS_PER_KM)

    if commits == 0 and distance_km > 0:
        commits = 1

    return commits


def create_commits_in_private_repo(repo_owner, repo_name, token, commit_count, activity_info):
    if commit_count == 0:
        print("No commits to create")
        return

    print("Syncing to private repo...")

    g = Github(token)
    repo = g.get_repo(f"{repo_owner}/{repo_name}")

    ref = repo.get_git_ref("heads/main")
    base_sha = ref.object.sha

    commit_shas = []
    for i in range(commit_count):
        blob = repo.create_git_blob(f"Fitness activity sync: {activity_info}\n", "utf-8")
        tree = repo.create_git_tree([InputGitTreeElement(
            path="activity.log",
            mode="100644",
            type="blob",
            sha=blob.sha
        )], base_tree=repo.get_git_tree(base_sha))
        commit = repo.create_git_commit(
            message=COMMIT_MESSAGE,
            tree=tree,
            parents=[repo.get_git_commit(base_sha)],
        )
        commit_shas.append(commit.sha)
        base_sha = commit.sha

    ref.edit(sha=base_sha)
    print("Done")


def main():
    print("=" * 50)
    print("GitFit - Fitness to GitHub Sync")
    print("=" * 50)

    target_date_arg = os.environ.get("TARGET_DATE")
    if target_date_arg:
        target_date = datetime.strptime(target_date_arg, "%Y-%m-%d").date()
    else:
        target_date = date.today() - timedelta(days=1)

    print("Querying Strava API...")

    access_token = get_strava_access_token()
    print("Got Strava access token")

    activities = get_activities(access_token, target_date)
    print(f"Processing activities...")

    if not activities:
        print("No activities to sync")
        return

    total_commits = 0
    for activity in activities:
        commits = calculate_commits(activity)
        total_commits += commits
        activity_info_for_commit = f"{activity.type}: {activity.name} ({activity.distance/1000:.1f}km)"

    repo_owner = os.environ.get("PRIVATE_REPO_OWNER")
    repo_name = os.environ.get("PRIVATE_REPO_NAME")
    repo_token = os.environ.get("PRIVATE_REPO_TOKEN")

    if not all([repo_owner, repo_name, repo_token]):
        print("ERROR: Missing private repo configuration")
        sys.exit(1)

    create_commits_in_private_repo(
        repo_owner, repo_name, repo_token, total_commits, activity_info_for_commit
    )

    print("Sync complete!")


if __name__ == "__main__":
    main()
