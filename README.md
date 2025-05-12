# doxcord

**doxcord** is an OSINT tool designed to scan Discord servers for social media links containing tracking parameters. The tool can identify Instagram, TikTok, and Facebook links that include tracking identifiers, and organize them by user and server.

*This tool was developed as part of the rump for the OSINT-FR MeetUp in Bordeaux on 22/05/2025. You can find the slides by clicking: [here](https://github.com/boringthegod/doxcord/blob/master/slides_MeetUp_OSINT-FR_Bordeaux_22052025.pdf)*

## Features

- Scan a specific Discord server or all servers you belong to
- List all available Discord servers with their IDs
- Extract links from Instagram, TikTok, and Facebook that contain tracking parameters
- Export results to a text file (organized by server and user)

## Installation

### Prerequisites

- Python 3.6+
- A Discord account token
- discord.py-self development version

### Setup

1. Clone the repository:
```bash
git clone https://github.com/boringthegod/doxcord.git
cd doxcord
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Install discord.py-self (required for user account access):
```bash
git clone https://github.com/dolfies/discord.py-self
cd discord.py-self
python -m pip install -U .[voice]
cd ..
```

## Usage

Before running the script, you need to set your Discord token:

```bash
export DISCORD_TOKEN='YOUR_DISCORD_TOKEN_HERE'
```

### How to obtain your Discord token

The discord.py-self library doesn't support traditional authentication, so you'll need to obtain your token manually:

**Easy method**: Paste this into the Discord client developer console (CTRL+SHIFT+I):
```javascript
(webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m => m?.exports?.default?.getToken).exports.default.getToken()
```

**Manual method**:
1. Open developer tools (CTRL+SHIFT+I)
2. Click the Network tab
3. Click the XHR tab
4. Select a request and click the Headers tab
5. Copy-paste the value in the Authorization header

### Command line arguments

```
usage: python doxcord.py [-h] (-ls | -gid GUILD_ID | -all) [-outfile OUTFILE] [--limit LIMIT]

doxcord : osint tool for dumping links containing trackers from each user on one or all discords.

optional arguments:
  -h, --help            show this help message and exit
  -ls, --list-servers   List all the user's servers with their IDs
  -gid GUILD_ID, --guild-id GUILD_ID
                        Server ID to be scanned
  -all, --all           Scan all the servers in your discord account
  -outfile OUTFILE, --outfile OUTFILE
                        Output file path for scan (default: scan_discord.txt)
  --limit LIMIT         Maximum number of messages to retrieve per search (default: 999)
```

### Examples

List all servers you belong to:
```bash
python doxcord.py --list-servers
```

Scan a specific server:
```bash
python doxcord.py --guild-id 123456789012345678
```

Scan all servers with a custom output file:
```bash
python doxcord.py --all --outfile results.txt
```

Scan a server with a custom message limit:
```bash
python doxcord.py --guild-id 123456789012345678 --limit 2000
```

## Output

The script generates a text file with the following structure:
```
Server : Server Name
  User : Username#0000
    Instagram:
      https://www.instagram.com/post/...?igsh=...
    Tiktok:
      https://vm.tiktok.com/...
    Facebook:
      https://www.facebook.com/...?mibextid=...

Server : Another Server
  ...
```

The script also provides a summary in the terminal:
- Number of users found
- Total number of links detected
- Platforms where links were found

## Current platforms dumped

| Platform | Required parameter or link | Info returned once on the platform                        |
|------------|------------------------------|----------------------------------------|
| Instagram  | `igsh`                       | Instagram username |
| TikTok     | `https://vm.tiktok.com`      | TikTok username       |
| Facebook   | `?mibextid=`                 | First and last name on Facebook     |

Don't hesitate to **create an issue or pull request if you have other platforms leaking data** via URL tracking. I'll add them and update the tool.

## Disclaimer

This tool is for educational purposes only. Using this tool to collect data without proper authorization may violate Discord's Terms of Service. Please use responsibly and ethically.

## Credits 

[dolfies/discord.py-self](https://github.com/dolfies/discord.py-self) – Python self-bot library.

[Textualize/Rich](https://github.com/Textualize/rich) – gorgeous terminal formatting.
