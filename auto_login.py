import asyncio
import os
import base64
from playwright.async_api import async_playwright

LOGIN_URL = "https://2pink.org/"
USERNAME  = os.environ["USERNAME_2PINK"]
PASSWORD  = os.environ["PASSWORD_2PINK"]

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(LOGIN_URL)
        await page.wait_for_load_state("networkidle")

        # Chụp ảnh trước khi click
        await page.screenshot(path="before_click.png")
        print("📸 Chụp ảnh trước click xong")

        # Click đăng nhập
        await page.click("text=Đăng nhập")
        await page.wait_for_timeout(3000)

        # Chụp ảnh sau khi click
        await page.screenshot(path="after_click.png")
        print("📸 Chụp ảnh sau click xong")

        # In ra toàn bộ HTML để xem selector
        html = await page.content()
        # Tìm các input fields
        inputs = await page.locator("input").all()
        print(f"🔍 Số lượng input tìm thấy: {len(inputs)}")
        for i, inp in enumerate(inputs):
            try:
                id_val   = await inp.get_attribute("id") or ""
                name_val = await inp.get_attribute("name") or ""
                type_val = await inp.get_attribute("type") or ""
                print(f"  Input {i}: id='{id_val}' name='{name_val}' type='{type_val}'")
            except:
                pass

        await browser.close()

asyncio.run(run())
