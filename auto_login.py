import asyncio
import os
from playwright.async_api import async_playwright

LOGIN_URL     = "https://2pink.org/"
DASHBOARD_URL = "https://2pink.org/dashboard/live-traffic"
USERNAME      = os.environ["accmoiq10@gmail.com"]
PASSWORD      = os.environ["27101992Long@"]

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(LOGIN_URL)
        await page.wait_for_load_state("networkidle")

        await page.click("text=Đăng nhập")
        await page.wait_for_timeout(1500)

        await page.fill("input[name='ctl00$ContentPlaceHolder1$ucDangNhap$txtTenDangNhap']", USERNAME)
        await page.fill("input[name='ctl00$ContentPlaceHolder1$ucDangNhap$txtMatKhau']", PASSWORD)
        await page.click("input[name='ctl00$ContentPlaceHolder1$ucDangNhap$btnDangNhap']")
        await page.wait_for_load_state("networkidle")
        print("✅ Đã đăng nhập!")

        await page.goto(DASHBOARD_URL)
        await page.wait_for_load_state("networkidle")

        toggle = page.locator("input[type='checkbox'].toggle, .toggle-checkbox, input[role='switch']").first
        is_checked = await toggle.is_checked()
        if not is_checked:
            await toggle.click()
            await page.wait_for_timeout(1000)
            print("✅ Đã bật Active Domain!")
        else:
            print("ℹ️ Active Domain đã bật sẵn rồi!")

        await browser.close()

asyncio.run(run())
