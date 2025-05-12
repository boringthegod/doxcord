#!/usr/bin/env python3
import discord
import argparse
import os
import sys
import re
import signal
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

banner = Text("doxcord", justify="center", style="bold white")
console.print(Panel(banner, expand=False, border_style="bright_blue"))

parser = argparse.ArgumentParser(
    description="doxcord : osint tool for dumping links containing trackers from each user on one or all discords."
)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    "-ls", "--list-servers",
    action="store_true",
    help="List all the user's servers with their IDs"
)
group.add_argument(
    "-gid", "--guild-id",
    type=int,
    help="Server ID to be scanned"
)
group.add_argument(
    "-all", "--all",
    action="store_true",
    help="Scan all the servers in your discord account"
)
parser.add_argument(
    "-outfile", "--outfile",
    default="scan_discord.txt",
    help="Output file path for scan (default: scan_discord.txt)"
)
parser.add_argument(
    "--limit",
    type=int,
    default=999,
    help="Maximum number of messages to retrieve per search (default: 999)"
)
args = parser.parse_args()

SEARCH_LIMIT = args.limit
OUT_PATH = args.outfile

USER_TOKEN = os.getenv("DISCORD_TOKEN") or "YOUR_TOKEN_HERE"
if USER_TOKEN in ("", "YOUR_TOKEN_HERE"):
    console.print("[red]Error[/]: define your Discord token via DISCORD_TOKEN or in USER_TOKEN.")
    sys.exit(1)

SEARCH_TERMS = {
    "instagram": "https://www.instagram.com/ igsh",
    "tiktok":    "https://vm.tiktok.com",
    "facebook":  "?mibextid="
}

URL_REGEX = {
    "instagram": re.compile(r'https?://(?:www\.)?instagram\.com/[^\s<>\"]+'),
    "tiktok":    re.compile(r'https?://vm\.tiktok\.com/[^\s<>\"]+'),
    "facebook":  re.compile(r'https?://(?:www\.)?facebook\.com/[^\s<>\"]*\?mibextid=[^\s<>\"]+')
}

class BotClient(discord.Client):
    async def on_ready(self):
        console.print(f"✅ Connected as [bold]{self.user}[/] (ID: {self.user.id})\n")

        if args.list_servers:
            console.print("📋 List of servers to which you belong :\n")
            for g in self.guilds:
                console.print(f"- [green]{g.name}[/] (ID: {g.id})")
            await self.close()
            os.kill(os.getpid(), signal.SIGINT)
            return

        if args.all:
            targets = self.guilds
            console.print(f"🔎 Scanning all servers ([bold]{len(targets)}[/] au total)\n")
        else:
            guild = self.get_guild(args.guild_id)
            if not guild:
                console.print(f"[red]Error[/]: Unable to find the server ID={args.guild_id}.")
                await self.close()
                os.kill(os.getpid(), signal.SIGINT)
                return
            targets = [guild]
            console.print(f"🔎 Server scan '[bold]{guild.name}[/]' (ID: {guild.id})\n")

        results = {}
        total_links = 0
        for guild in targets:
            console.print(f"--- Server : [blue]{guild.name}[/] (ID: {guild.id}) ---")
            per_user = {}
            for site, query in SEARCH_TERMS.items():
                console.print(f"-- Search [yellow]{site.upper()}[/]: '{query}' (limit={SEARCH_LIMIT})")
                try:
                    async for msg in guild.search(query, limit=SEARCH_LIMIT):
                        author = str(msg.author)
                        per_user.setdefault(author, {k: set() for k in SEARCH_TERMS})
                        for url in URL_REGEX[site].findall(msg.content):
                            per_user[author][site].add(url)
                except AttributeError:
                    console.print("⚠️ ERROR : your version of discord.py-self does not support guild.search().")
                    break
                except discord.HTTPException as e:
                    console.print(f"⚠️ HTTPException on {site}: {e}")
                except discord.Forbidden:
                    console.print(f"⚠️ Forbidden on {site}: insufficient permissions.")
                except Exception as e:
                    console.print(f"⚠️ Unexpected error ({site}): {e}")

            for author, sites in per_user.items():
                for urls in sites.values():
                    total_links += len(urls)
            results[guild.name] = per_user
            console.print()

        with open(OUT_PATH, "w", encoding="utf-8") as f:
            for guild_name, per_user in results.items():
                f.write(f"Server : {guild_name}\n")
                for author, sites in per_user.items():
                    if any(sites[s] for s in sites):
                        f.write(f"  User : {author}\n")
                        for site in ("instagram", "tiktok", "facebook"):
                            if sites[site]:
                                f.write(f"    {site.capitalize()}:\n")
                                for url in sorted(sites[site]):
                                    f.write(f"      {url}\n")
                f.write("\n")

        users_found = sum(
            1
            for per_user in results.values()
            for sites in per_user.values()
            if any(sites.values())
        )
        platforms_used = [plat.capitalize() for plat in SEARCH_TERMS if any(
            results[g][u][plat]
            for g in results
            for u in results[g]
        )]
        console.print(
            f":tada: [bold]{users_found}[/] users found, "
            f"[bold]{total_links}[/] total links on the platforms : [bold]{', '.join(platforms_used)}[/]"
        )

        console.print(f"✅ Scan completed. Results written in '[bold]{OUT_PATH}[/]'.")
        await self.close()
        os.kill(os.getpid(), signal.SIGINT)

if __name__ == "__main__":
    client = BotClient()
    try:
        client.run(USER_TOKEN, reconnect=False)
    except KeyboardInterrupt:
        console.print("✋ Script completed.")
    except discord.LoginFailure:
        console.print("❌ CONNECTION ERROR: invalid token.")
    except Exception as e:
        console.print(f"❌ Unexpected error : {e}")
