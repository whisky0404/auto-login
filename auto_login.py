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

        # 1. Vào trang chủ
        await page.goto(LOGIN_URL)
        await page.wait_for_load_state("networkidle")

        # 2. Click nút Đăng nhập để mở popup
        await page.click("text=Đăng nhập")
        await page.wait_for_timeout(2000)

        # 3. Chờ popup hiện ra rồi mới fill
        await page.wait_for_selector("input[id*='TenDangNhap']", timeout=10000)
        await page.fill("input[id*='TenDangNhap']", USERNAME)
        await page.fill("input[id*='MatKhau']", PASSWORD)

        # 4. Click nút đăng nhập trong popup
        await page.click("input[id*='btnDangNhap']")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        print("✅ Đã đăng nhập!")

        # 5. Vào dashboard Live Traffic
        await page.goto(DASHBOARD_URL)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)

        # 6. Bật toggle Active Domain nếu đang tắt
        try:
            toggle = page.locator("input[type='checkbox']").first
            is_checked = await toggle.is_checked()
            if not is_checked:
                await toggle.click()
                await page.wait_for_timeout(1000)
                print("✅ Đã bật Active Domain!")
            else:
                print("ℹ️ Active Domain đã bật sẵn rồi!")
        except Exception as e:
            print(f"⚠️ Không tìm thấy toggle: {e}")

        await browser.close()

asyncio.run(run())
