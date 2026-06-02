import asyncio
import os
from playwright.async_api import async_playwright

LOGIN_URL     = "https://2pink.org/"
DASHBOARD_URL = "https://2pink.org/dashboard/live-traffic"
USERNAME      = os.environ["USERNAME_2PINK"]
PASSWORD      = os.environ["PASSWORD_2PINK"]
ACTION        = os.environ.get("ACTION", "on")  # "on" hoặc "off"

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

        try:
            checkbox = page.locator("input[type='checkbox']").first
            checkbox_id = await checkbox.get_attribute("id")
            is_checked = await page.evaluate(f"document.getElementById('{checkbox_id}').checked")

            if ACTION == "on" and not is_checked:
                await page.evaluate(f"document.getElementById('{checkbox_id}').click()")
                await page.wait_for_timeout(1000)
                print("✅ Đã BẬT Active Domain!")
            elif ACTION == "off" and is_checked:
                await page.evaluate(f"document.getElementById('{checkbox_id}').click()")
                await page.wait_for_timeout(1000)
                print("✅ Đã TẮT Active Domain!")
            else:
                print(f"ℹ️ Active Domain đã ở trạng thái {'bật' if is_checked else 'tắt'} rồi, không cần thay đổi.")
        except Exception as e:
            print(f"⚠️ Lỗi toggle: {e}")

        await browser.close()

asyncio.run(run())
