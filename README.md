# GitFit

Are you tired of seeing my contribution chart light up only when you write code?

I am, personally. And I'm tired of that in particular when I'm investing that time in equally virtuous and poritive activities than coding. Virtuous for my physical and mental health, of course.

**GitFit** syncs your fitness activities from Strava to your GitHub contribution graph — without exposing your private workout data to the world.

## Overview

This project automatically fetches your Strava activities and creates corresponding commits in a private repository. Your contribution graph shows your fitness activity, while your actual workout data remains hidden in a private repo.

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  PUBLIC REPO (this repo)                                    │
│  - Contains the sync code and workflow                      │
│  - Open source for community                                │
└─────────────────────────────────────────────────────────────┘
                              │
        Push commits via PAT  │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  PRIVATE REPO (fitness-contributions)                       │
│  - Contains activity data commits                           │
│  - Shows as private contributions on your profile           │
└─────────────────────────────────────────────────────────────┘
```

**Important**: Enable private contributions on your GitHub profile:
1. Go to https://github.com/settings/profile
2. Check "Include private contributions on my profile"



## Features

- **Automatic sync**: Runs daily via cron or on-demand via manual trigger
- **Multiple commits per activity**: Based on distance and duration
- **Private by default**: All fitness data stays in a private repo
- **Open source**: This code is public and shareable



## Setup Guide

### Prerequisites

- A Strava account
- A GitHub account
- Two GitHub repositories:
  - **Public**: For this code (the one you're viewing)
  - **Private**: For contribution commits


### Step 1: Create a Strava API Application

1. Go to https://www.strava.com/settings/api
2. Create an application:
   - **Application Name**: GitFit
   - **Category**: Other
   - **Website**: https://github.com/yourusername/your-public-repo
   - **Authorization Callback Domain**: localhost
3. Note down your:
   - **Client ID**
   - **Client Secret**


### Step 2: Get Your Refresh Token

You'll need a one-time OAuth flow to get a refresh token. Run this locally:

```bash
# Set your Strava credentials
export STRAVA_CLIENT_ID="your_client_id"
export STRAVA_CLIENT_SECRET="your_client_secret"

# Open browser to authorize
python3 -c "
import webbrowser
import os

client_id = os.environ['STRAVA_CLIENT_ID']
redirect_uri = 'http://localhost'
url = f'https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&approval_prompt=force&scope=activity:read_all'
webbrowser.open(url)
print('After authorizing, copy the code from the URL (code=...)')
"

# Exchange code for tokens (replace CODE with the code from the URL)
curl -X POST https://www.strava.com/api/v3/oauth/token \
  -d client_id=$STRAVA_CLIENT_ID \
  -d client_secret=$STRAVA_CLIENT_SECRET \
  -d code=YOUR_AUTHORIZATION_CODE \
  -d grant_type=authorization_code
```

Copy the `refresh_token` from the response. This token doesn't expire.



### Step 3: Create Private Repo for Contributions

1. Create a new private repository: https://github.com/new
2. Name it `fitness-contributions` (or whatever you prefer)
3. Make it **Private**
4. Do NOT initialize with any files



### Step 4: Generate GitHub Personal Access Token

1. Go to https://github.com/settings/tokens/new
2. Generate a new token (classic) with:
   - **Note**: "GitFit"
   - **Expiration**: No expiration (or your preference)
   - **Scopes**: Select `repo` (full control of private repositories)
3. Copy the generated token



### Step 5: Configure Secrets

In your **public** repository:

1. Go to Settings → Secrets and variables → Actions
2. Add these secrets:

| Secret Name | Value |
|-|-|
| `STRAVA_CLIENT_ID` | Your Strava Client ID |
| `STRAVA_CLIENT_SECRET` | Your Strava Client Secret |
| `STRAVA_REFRESH_TOKEN` | Your refresh token from Step 2 |
| `PRIVATE_REPO_TOKEN` | Your GitHub PAT from Step 4 |
| `PRIVATE_REPO_OWNER` | Your GitHub username |
| `PRIVATE_REPO_NAME` | Name of your private repo (e.g., `fitness-contributions`) |



### Step 6: Enable Private Contributions

1. Go to https://github.com/settings/profile
2. Check "Include private contributions on my profile"
3. Save


## How Activity Maps to Commits

The sync creates multiple commits per activity based on intensity:

| Activity Distance | Commits Created |
|-|--|
| < 2 km | 1 commit |
| 2-5 km | 2 commits |
| 5-10 km | 3 commits |
| 10-20 km | 4 commits |
| 20+ km | 5 commits |

Each commit represents 1 unit of intensity. This creates a more expressive contribution graph that reflects workout intensity.



## Usage

### Automatic Sync

The workflow runs automatically every day at 6:00 UTC. You can modify this in `.github/workflows/sync-fitness.yml`.

### Manual Trigger

You can manually trigger a sync:
1. Go to the Actions tab in your public repo
2. Select "Sync Fitness Activities"
3. Click "Run workflow"

### Checking Results

1. Visit your private repo to see the commits
2. Your contribution graph on your profile shows green squares



## Customization

### Adjust Commit Mapping

Edit `COMMITS_PER_KM` in `scripts/sync.py`:

```python
COMMITS_PER_KM = 1  # commits per km of activity
```

### Change Schedule

Edit the cron in `.github/workflows/sync-fitness.yml`:

```yaml
schedule:
  - cron: '0 6 * * *'  # daily at 6:00 UTC
```



## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── sync-fitness.yml    # GitHub Actions workflow
├── scripts/
│   └── sync.py                 # Main sync script
├── .env.example                # Environment template
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore patterns
└── README.md                  # This file
```



## Troubleshooting

### "No activities found"

- Check that you have activities on Strava
- Verify your refresh token is valid

### "Authentication error"

- Re-check your Strava secrets
- Ensure your refresh token hasn't been revoked

### Commits not appearing on profile

- Verify "Include private contributions" is enabled
- Check that the private repo exists and is accessible with your PAT



## License

MIT License - feel free to use and modify!



## Contributing

Contributions are welcome! Please open an issue or submit a PR.
