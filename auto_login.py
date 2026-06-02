import asyncio
import os
from playwright.async_api import async_playwright

LOGIN_URL     = "https://2pink.org/"
DASHBOARD_URL = "https://2pink.org/dashboard/live-traffic"
USERNAME      = os.environ["USERNAME_2PINK"]
PASSWORD      = os.environ["PASSWORD_2PINK"]

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(LOGIN_URL)
        await page.wait_for_load_state("networkidle")

        await page.click("text=Đăng nhập")
        await page.wait_for_timeout(2000)

        await page.fill("#ctl00_ContentPlaceHolder1_txtUserName", USERNAME)
        await page.fill("#ctl00_ContentPlaceHolder1_txtPass", PASSWORD)
        await page.click("#ctl00_ContentPlaceHolder1_btnDangNhap")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        print("✅ Đã đăng nhập!")

        await page.goto(DASHBOARD_URL)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)

        # Toggle ẩn → cần check qua JS rồi click label
        try:
            checkbox = page.locator("input[type='checkbox']").first
            checkbox_id = await checkbox.get_attribute("id")
            is_checked = await page.evaluate(f"document.getElementById('{checkbox_id}').checked")

            if not is_checked:
                # Click label tương ứng thay vì checkbox
                await page.evaluate(f"document.getElementById('{checkbox_id}').click()")
                await page.wait_for_timeout(1000)
                print("✅ Đã bật Active Domain!")
            else:
                print("ℹ️ Active Domain đã bật sẵn rồi!")
        except Exception as e:
            print(f"⚠️ Lỗi toggle: {e}")

        await browser.close()

asyncio.run(run())
