# Discord Team Bot

A Discord slash-command bot for managing private team member roles/channels, strikes, RP warnings, and removals.

## Commands

- `/addmember` - Creates a private role and private channel for a selected member under either the Events or Parties category.
- `/strike` - Gives a member a strike, DMs them, and logs it in the strikes channel. Members are removed at 2/2 strikes.
- `/rpwarning` - Gives a member an RP warning, DMs them, and logs it in the warnings channel. Members are removed at 3/3 RP warnings.
- `/removemember` - Deletes the selected member's saved private role and channel.

## Local Setup

### 1. Install Python

Install Python 3.10 or newer.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create your `.env` file

Copy `.env.example` and rename it to `.env`.

Fill in:

```env
DISCORD_TOKEN=your_bot_token
GUILD_ID=your_server_id
EVENTS_CATEGORY_ID=your_events_category_id
PARTIES_CATEGORY_ID=your_parties_category_id
STRIKES_CHANNEL_ID=your_strikes_log_channel_id
WARNINGS_CHANNEL_ID=your_warnings_log_channel_id
```

### 4. Enable Discord Developer Mode

In Discord:

1. User Settings
2. Advanced
3. Enable Developer Mode

Then right-click your server, categories, and channels to copy their IDs.

### 5. Run the bot

```bash
python bot.py
```

## Discord Developer Portal Setup

1. Go to the Discord Developer Portal.
2. Create a New Application.
3. Go to Bot.
4. Click Add Bot.
5. Copy the bot token into your `.env` file.
6. Enable these Privileged Gateway Intents:
   - Server Members Intent

## Invite Bot to Your Server

In the Developer Portal:

1. Go to OAuth2 > URL Generator.
2. Select scopes:
   - `bot`
   - `applications.commands`
3. Select bot permissions:
   - Manage Roles
   - Manage Channels
   - Send Messages
   - View Channels
   - Read Message History
   - Use Slash Commands
4. Open the generated URL and invite the bot.

Important: Move the bot role above any roles it needs to manage.

## GitHub Setup

1. Create a new GitHub repository.
2. Upload all files except `.env`.
3. Do not upload your `.env` file because it contains your private bot token.
4. Keep `.env.example` uploaded so you know which variables are needed.

## Hosting Notes

GitHub stores the code, but it does not keep your bot online by itself. To keep the bot online, host it on a service like Railway, Render, Replit, a VPS, or your own computer.

When hosting, add your `.env` values as environment variables/secrets in your host's dashboard.
"# discord_team_bot" 
