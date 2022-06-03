import argparse
import sys

SITES = {
    "footlocker": "http://www.footlocker.com/",
    "champssports": "http://www.champssports.com/",
    "kidsfootlocker": "http://www.kidsfootlocker.com/",
    "eastbay": "http://www.eastbay.com/",
}


def parse_cli(args):
    parser = argparse.ArgumentParser(
        description="Auto login web scraper for logging in and adding user and payment details."
    )

    instruction = parser.add_mutually_exclusive_group()
    instruction.add_argument("--verify-only", dest="verify_only", action="store_true")
    instruction.add_argument(
        "--update-user-only", dest="update_user_only", action="store_true"
    )
    instruction.add_argument(
        "--update-cc-only", dest="update_cc_only", action="store_true"
    )

    subparsers = parser.add_subparsers()
    subparsers.metavar = "subcommand"

    file = subparsers.add_parser(
        "file",
        help="If you are suppling a CSV file with user/payment info and websites of interest.",
    )

    file.add_argument(
        "--name",
        "-n",
        dest="config_file",
        default=None,
        required=True,
        metavar="",
        help="Add config.csv file containing user info, card info, and sites to target.",
    )

    parser.add_argument(
        "--discord",
        dest="discord_url",
        type=str,
        help="Enter discord url for alerting.",
        default=None,
    )

    parser.add_argument(
        "--proxy-url",
        dest="proxy_url",
        type=str,
        help="Enter proxy url",
    )

    parser.add_argument(
        "--proxy-user",
        dest="proxy_user",
        required="--proxy-url" in sys.argv,
        help="Enter proxy username",
    )

    parser.add_argument(
        "--proxy-pass",
        dest="proxy_pass",
        required="--proxy-url" in sys.argv,
        help="Enter proxy password",
    )

    parser.add_argument(
        "--site",
        "-s",
        dest="sites",
        choices=SITES.keys(),
        default=SITES,
        metavar="",
        help=f"Choose desired site. Checks all by default. Choices: {list(SITES.keys())}",
    )

    parser.add_argument(
        "--url",
        dest="url",
        choices=SITES.values(),
        metavar="",
        help=f"Choose desired url. Choices: {list(SITES.values())}",
    )

    parser.add_argument(
        "--user",
        "-u",
        dest="user",
        action="store_true",
        default="shivani.patel823@gmail.com",
        help="Enter email or username used to login",
    )

    parser.add_argument(
        "--pwd",
        "-p",
        dest="pwd",
        default="#Cc5ot!o6xBg",
        required="--user" in sys.argv,
        metavar="",
        help="Enter password used to login",
    )

    parser.add_argument(
        "--first-name",
        "-fname",
        dest="fname",
        default="krista",
        required="--user" in sys.argv,
        metavar="",
        help="User's first name",
    )

    parser.add_argument(
        "--last-name",
        "-lname",
        dest="lname",
        default="marmol",
        required="--user" in sys.argv,
        metavar="",
        help="User's last name",
    )

    parser.add_argument(
        "--phone-number",
        "-phone",
        dest="telephone",
        default="8128675309",
        required="--user" in sys.argv,
        metavar="",
        help="User's telephone number",
    )

    parser.add_argument(
        "--street-address",
        "-addr",
        dest="addr",
        default="47711",
        required="--user" in sys.argv,
        metavar="",
        help="User's street address (City and State are auto populated in the site when zip code is entered.)",
    )
    parser.add_argument(
        "--zipcode",
        "-zip",
        dest="zipcode",
        default="47711",
        required="--user" in sys.argv,
        metavar="",
        help="User's zip code",
    )

    parser.add_argument(
        "--card_number",
        "-cn",
        dest="card_number",
        default="4242424242424242",
        action="store_true",
        help="Enter card number",
    )

    parser.add_argument(
        "--card_month",
        "-cm",
        dest="card_month",
        required="--card_number" in sys.argv,
        default="12",
        metavar="",
        help="Enter card experation month",
    )

    parser.add_argument(
        "--card_year",
        "-cy",
        dest="card_year",
        required="--card_number" in sys.argv,
        default="25",
        metavar="",
        help="Enter card experation year",
    )

    parser.add_argument(
        "--card_cvv",
        "-ccv",
        dest="card_cvv",
        required="--card_number" in sys.argv,
        default="123",
        metavar="",
        help="Enter card CVV (3 digit code on the back)",
    )

    parser.add_argument(
        "--test",
        dest="test",
        action="store_true",
        help="Used for setting test parameters that won't cost TextVerify credits.",
    )

    return parser.parse_args(args)
