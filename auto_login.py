ACTION = os.environ.get("ACTION", "on")  # "on" hoặc "off"

# Thay phần try/except toggle bằng:
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
