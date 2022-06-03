from discordwebhook import Discord

DISCORD_URL = None


def discord_webhook(msg):

    if DISCORD_URL is not None:
        discord = Discord(url=DISCORD_URL)
        discord.post(
            embeds=[
                {
                    "title": "Breaking News With Your Script!!",
                    "description": msg,
                    "footer": {},
                }
            ],
        )
