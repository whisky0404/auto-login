import asyncio
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from playwright.async_api import async_playwright

LOGIN_URL     = "https://2pink.org/"
DASHBOARD_URL = "https://2pink.org/dashboard/live-traffic"
USERNAME      = os.environ["USERNAME_2PINK"]
PASSWORD      = os.environ["PASSWORD_2PINK"]
ACTION        = os.environ.get("ACTION", "on")
ACCOUNT       = os.environ.get("ACCOUNT", "?")

GMAIL_USER    = os.environ.get("GMAIL_USER", "")
GMAIL_PASS    = os.environ.get("GMAIL_APP_PASSWORD", "")

logs = []

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry)
    logs.append(entry)

def send_email(success: bool):
    if not GMAIL_USER or not GMAIL_PASS:
        print("⚠️ Chưa cấu hình Gmail, bỏ qua gửi email.")
        return

    status = "✅ Thành công" if success else "❌ Thất bại"
    action_text = "BẬT" if ACTION == "on" else "TẮT"
    subject = f"[2Pink] Account {ACCOUNT} - {action_text} - {status}"

    body = f"""
<h2>2Pink Auto Active - Báo cáo</h2>
<table border="1" cellpadding="6" cellspacing="0">
  <tr><td><b>Tài khoản</b></td><td>Account {ACCOUNT}</td></tr>
  <tr><td><b>Hành động</b></td><td>{action_text}</td></tr>
  <tr><td><b>Trạng thái</b></td><td>{status}</td></tr>
  <tr><td><b>Thời gian</b></td><td>{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</td></tr>
</table>
<h3>Chi tiết log:</h3>
<pre>{"<br>".join(logs)}</pre>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = GMAIL_USER
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())
        print("📧 Đã gửi email báo cáo!")
    except Exception as e:
        print(f"⚠️ Lỗi gửi email: {e}")

async def run():
    success = False
    try:
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
            log("✅ Đã đăng nhập!")

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
                    log("✅ Đã BẬT Active Domain!")
                    success = True
                elif ACTION == "off" and is_checked:
                    await page.evaluate(f"document.getElementById('{checkbox_id}').click()")
                    await page.wait_for_timeout(1000)
                    log("✅ Đã TẮT Active Domain!")
                    success = True
                else:
                    log(f"ℹ️ Active Domain đã ở trạng thái {'bật' if is_checked else 'tắt'} rồi, không cần thay đổi.")
                    success = True
            except Exception as e:
                log(f"⚠️ Lỗi toggle: {e}")

            await browser.close()

    except Exception as e:
        log(f"❌ Lỗi nghiêm trọng: {e}")

    send_email(success)

asyncio.run(run())
