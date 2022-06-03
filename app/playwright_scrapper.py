from playwright.async_api import Playwright, TimeoutError
from tqdm import tqdm
from text_verify import MakeApiCall
from discord import discord_webhook


async def app(playwright: Playwright, app_data):
    if "proxy_info" in app_data:
        print("Connecting to proxy...")
        browser = await playwright.chromium.launch(proxy=app_data["proxy_info"])
    else:
        browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    for site_name,site_url in app_data["args"].sites.items():

        if "file_data" in app_data:
            for i in tqdm(app_data["file_data"], colour="cyan"):
                if app_data["file_data"][i][site_url] == "x":
                    email = app_data["file_data"][i]["email"]
                    fname = app_data["file_data"][i]["first_name"]
                    lname = app_data["file_data"][i]["last_name"]
                    passwd = app_data["file_data"][i]["password"]
                    telephone = app_data["file_data"][i]["telephone"]
                    street_addr = app_data["file_data"][i]["street_address"]
                    zip = app_data["file_data"][i]["zip_code"]
                    # default_shipping = app_data["file_data"][i]["default_shipping"]
                    # default_billing = app_data["file_data"][i]["default_billing"]
                    card_number = app_data["file_data"][i]["card_number"]
                    card_month = app_data["file_data"][i]["card_month"]
                    card_year = app_data["file_data"][i]["card_year"]
                    card_cvv = app_data["file_data"][i]["card_cvv"]


                                # begin scrape
                    page = await context.new_page()
                    await page.goto(site_url)
                    # give it time for the popup to appear
                    await page.wait_for_timeout(3000)

                    if app_data["args"].verify_only:
                        await login(email, passwd, page)
                    elif app_data["args"].update_user_only:
                        if await login(email, passwd, page) is False:
                            continue
                        else:
                            await page.locator("text=My Account").click()
                            await update_user_profile(
                                email, fname, lname, telephone, street_addr, zip, page
                            )

                    elif app_data["args"].update_cc_only:
                        if await login(email, passwd, page) is False:
                            continue
                        else:
                            await page.locator("text=My Account").click()
                            await update_cc_info(
                                card_number, card_month, card_year, card_cvv, page, site_url, site_name, app_data["args"].test
                            )

                    else:

                        if await login(email, passwd, page) is False:
                            continue
                        if app_data["args"].verify_only is True:
                            continue

                        await page.locator("text=My Account").click()
                        # await expect(page).to_have_url(f"{url}/account/details")
                        # Edit Account Info
                        await update_user_profile(
                            email, fname, lname, telephone, street_addr, zip, page
                        )

                        await update_cc_info(
                            card_number, card_month, card_year, card_cvv, page, site_url, site_name, app_data["args"].test
                        )
        else:

            email = app_data["args"].user
            fname = app_data["args"].fname
            lname = app_data["args"].lname
            passwd = app_data["args"].pwd
            telephone = app_data["args"].telephone
            street_addr = app_data["args"].addr
            zip = app_data["args"].zipcode
            # default_shipping = app_data["file_data"][i]["default_shipping"]
            # default_billing = app_data["file_data"][i]["default_billing"]
            card_number = app_data["args"].card_number
            card_month = app_data["args"].card_month
            card_year = app_data["args"].card_year
            card_cvv = app_data["args"].card_cvv

            # begin scrape
            page = await context.new_page()
            await page.goto(site_url)
            # give it time for the popup to appear
            await page.wait_for_timeout(3000)

            if app_data["args"].verify_only:
                await login(email, passwd, page)
            elif app_data["args"].update_user_only:
                if await login(email, passwd, page) is False:
                    continue
                else:
                    await page.locator("text=My Account").click()
                    await update_user_profile(
                        email, fname, lname, telephone, street_addr, zip, page
                    )

            elif app_data["args"].update_cc_only:
                if await login(email, passwd, page) is False:
                    continue
                else:
                    await page.locator("text=My Account").click()
                    await update_cc_info(
                        card_number, card_month, card_year, card_cvv, page, site_url, site_name, app_data["args"].test
                    )

            else:

                if await login(email, passwd, page) is False:
                    continue
                if app_data["args"].verify_only is True:
                    continue

                await page.locator("text=My Account").click()
                # await expect(page).to_have_url(f"{url}/account/details")
                # Edit Account Info
                await update_user_profile(
                    email, fname, lname, telephone, street_addr, zip, page
                )

                await update_cc_info(
                    card_number, card_month, card_year, card_cvv, page, site_url, site_name, app_data["args"].test
                )

    await context.close()
    await browser.close()
    print("Script Complete!")
    msg = "Script Complete!"
    discord_webhook(msg, app_data["args"].discord_url)


async def update_cc_info(card_number, card_month, card_year, card_cvv, page,site_url,site_name,test=False):

    print(f"Testing creds against: {site_url}")
    # target_name = app_data["site_ids"][site_name]
    api_call = MakeApiCall(site_name)
    if test == False:
        verifcation_data = api_call.post_create_verification()
        if verifcation_data == "Insufficient credits to start a verification.":
            exit(1)
    else:
        verifcation_data = api_call.get_data_from_file(
            file_name="current_verification.json"
        )
    phone_number = verifcation_data["number"]

     # Add credit card
    await page.locator("text=Add Card").click()
    await page.locator('input[name="otpPhone"]').click()
    await page.locator('input[name="otpPhone"]').fill(phone_number)
    await page.wait_for_timeout(1000)
    await page.locator("text=send code").click()
    verifcation_status_data = api_call.get_verification_status()
    sms = verifcation_status_data["sms"]
    code = sms.split(":")[1].strip()
    await page.locator('input[name="otpCode"]').fill(code)
    await page.wait_for_timeout(1000)
    await page.locator("text=Enter code").click()
    await page.frame_locator(
        "text=Card Number*<p>Your browser does not support iframes.</p>Card Number* >> iframe"
    ).locator('[aria-label="Credit or debit card number"]').click()
    await page.frame_locator(
        "text=Card Number*<p>Your browser does not support iframes.</p>Card Number* >> iframe"
    ).locator('[aria-label="Credit or debit card number"]').fill(card_number)
    await page.wait_for_timeout(1000)
    await page.frame_locator(
        "text=MM*<p>Your browser does not support iframes.</p>MM* >> iframe"
    ).locator('[aria-label="Credit or debit card expiration month - 2 digits"]').click()
    await page.frame_locator(
        "text=MM*<p>Your browser does not support iframes.</p>MM* >> iframe"
    ).locator('[aria-label="Credit or debit card expiration month - 2 digits"]').fill(
        card_month
    )
    await page.wait_for_timeout(1000)
    await page.frame_locator(
        "text=YY*<p>Your browser does not support iframes.</p>YY* >> iframe"
    ).locator('[aria-label="Credit or debit card expiration year - 2 digits"]').click()
    await page.frame_locator(
        "text=YY*<p>Your browser does not support iframes.</p>YY* >> iframe"
    ).locator('[aria-label="Credit or debit card expiration year - 2 digits"]').fill(
        card_year
    )
    await page.wait_for_timeout(1000)
    await page.frame_locator(
        "text=CSC*<p>Your browser does not support iframes.</p>CSC* >> iframe"
    ).locator('[aria-label="Credit or debit card CVC\\/CVV"]').click()
    await page.frame_locator(
        "text=CSC*<p>Your browser does not support iframes.</p>CSC* >> iframe"
    ).locator('[aria-label="Credit or debit card CVC\\/CVV"]').fill(card_cvv)
    await page.wait_for_timeout(1000)
    await page.locator("text=Save & Continue").nth(1).click()


async def update_user_profile(
    email, fname, lname, telephone, street_addr, zip, page
):
    await page.locator("text=Edit Account Info").click()
    await page.locator('input[name="firstName"]').click()
    await page.locator('input[name="firstName"]').fill(fname)
    await page.wait_for_timeout(1000)
    await page.locator('input[name="lastName"]').click()
    await page.locator('input[name="lastName"]').fill(lname)
    await page.wait_for_timeout(1000)
    await page.locator('input[name="email"]').click()
    await page.locator('input[name="email"]').fill(email)
    await page.wait_for_timeout(1000)
    await page.locator('input[name="phoneNumber"]').click()
    await page.locator('input[name="phoneNumber"]').fill(telephone)
    await page.wait_for_timeout(1000)
    await page.locator('input[name="postalCode"]').click()
    await page.locator('input[name="postalCode"]').fill(str(zip))
    await page.wait_for_timeout(1000)
    await page.locator("button", has_text="Save").nth(1).click()
    # Add Address
    await page.locator("text=Add Address").click()
    await page.locator(".c-form-field__indicator").first.click()
    await page.locator("div:nth-child(5) > label > .c-form-field__indicator").click()
    await page.locator(
        'div[role="dialog"] div:has-text("Country*Select a CountryAfghanistanAndorraAngolaAnguillaAntarcticaAntigua and Ba")'
    ).nth(2).click()
    await page.locator('input[name="firstName"]').click()
    await page.locator('input[name="firstName"]').fill(fname)
    await page.wait_for_timeout(1000)
    await page.locator('input[name="lastName"]').click()
    await page.locator('input[name="lastName"]').fill(lname)
    await page.wait_for_timeout(1000)
    await page.locator('input[name="line1"]').click()
    await page.locator('input[name="line1"]').fill(street_addr)
    await page.wait_for_timeout(1000)
    await page.locator('input[name="postalCode"]').click()
    await page.locator('input[name="postalCode"]').fill(str(zip))
    await page.wait_for_timeout(1000)
    await page.locator('input[name="phone"]').click()
    await page.locator('input[name="phone"]').fill(telephone)
    await page.wait_for_timeout(1000)
    await page.locator("text=Save Address").nth(1).click()
    await page.locator("text=Save & Continue").click()



async def login(email, passwd, page):
    try:
        await page.locator('#bluecoreActionScreen button:has-text("X")').click()
    except TimeoutError:
        print("No pop-ups to close")
        # Sign in
    await page.locator("text=Welcome, Sign In").click()
    # await page.locator('input[name="uid"]').click()
    await page.locator('input[name="uid"]').fill(email)
    await page.wait_for_timeout(1000)
    # await page.locator('input[name="password"]').click()
    await page.locator('input[name="password"]').fill(passwd)
    await page.wait_for_timeout(1000)
    await page.locator("text=Sign In").nth(3).click()

    # Allow time to authenticate
    await page.wait_for_timeout(5000)
    try:
        await page.locator("text=/Hi,\\s\\w+/i").click(timeout=300)
    except TimeoutError:
        await page.locator(
            'text=Sign InYour information contains 1 errorInvalid email and/or password. Please tr >> [aria-label="Close"]'
        ).click()
        print(
            f"Could not sign in with creds provided for user: {email}. Attempting next user..."
        )
        msg = f"Could not sign in with creds provided for user: {email}. Attempting next user..."
        discord_webhook(msg)
        return False
    else:
        return True
