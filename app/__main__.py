import asyncio
from playwright.async_api import async_playwright
from playwright_scrapper import app
from cli import parse_cli
import pandas as pd
from signal import signal, SIGINT
from sys import exit
from web_scraper.discord import discord_webhook
from web_scraper import discord


def handler(signal_received, frame):
    # Handle any cleanup here
    print("\nCTRL-C detected. Exiting grac`efully")
    exit(0)


async def main(args_switch=None):
    app_data = {}
    app_data["args"] = parse_cli(args_switch)

    if app_data["args"].discord_url is not None:
        discord.DISCORD_URL = app_data["args"].discord_url

    if app_data["args"].proxy_url is not None:
        proxy = {}
        proxy["server"] = app_data["args"].proxy_url
        proxy["username"] = app_data["args"].proxy_user
        proxy["password"] = app_data["args"].proxy_pass
        app_data["proxy_info"] = proxy

    stringified_urls = " ".join([f"{v}" for v in app_data["args"].sites.values()])
    print(f"Logging into sites: {stringified_urls}")
    print(f"User: {app_data['args'].user} --- Run script with -u option to change.")
    print(f"Password: {app_data['args'].pwd} --- Run script with -p option to change.")

    try:
        if app_data["args"].config_file:
            df = pd.read_csv(app_data["args"].config_file)
            file_data = df.to_dict("index")
            app_data["file_data"] = file_data
    except AttributeError as ex:
        print(ex)
        pass

    try:
        async with async_playwright() as playwright:
            await app(playwright, app_data)
    except Exception as ex:
        print(f"There was an error running application. {ex}")
        discord_webhook(f"There was an error running application. {ex}")


if __name__ == "__main__":
    # run the handler() function when SIGINT is recieved
    signal(SIGINT, handler)
    asyncio.run(main())
