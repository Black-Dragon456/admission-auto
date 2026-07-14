import os
from datetime import datetime

from playwright.sync_api import sync_playwright

import captcha
import config


def write_log(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{now}] {message}")

    with open(
            os.path.join(config.LOGS_DIR, "result.log"),
            "a",
            encoding="utf-8"
    ) as f:
        f.write(f"[{now}] {message}\n")


def save_screenshot(page):
    filename = datetime.now().strftime("%Y%m%d_%H%M%S")

    path = os.path.join(config.SCREENSHOT_DIR, f"{filename}.png")

    # 截取查询结果区域
    result_area = page.locator(".cen-form")

    result_area.screenshot(path=path)

    print(f"截图保存：{path}")


def parse_result(page):
    """
    根据tab激活状态判断结果
    enresult1 = 有录取
    enresult2 = 暂无录取
    """

    # 有录取信息
    if page.locator("#enresult1.tab-pane.active").count() == 0:
        result = {
            "考生状态": page.locator("#enresult1 .lqzt").inner_text().strip(),
            "院校代号": page.locator("#enresult1 .yxdh").inner_text().strip(),
            "院校名称": page.locator("#enresult1 .yxmc").inner_text().strip(),
            "专业组名称": page.locator("#enresult1 .zyzmc").inner_text().strip(),
            "专业代号": page.locator("#enresult1 .zydh").inner_text().strip(),
            "专业名称": page.locator("#enresult1 .zymc").inner_text().strip(),
            "批次名称": page.locator("#enresult1 .pcmc").inner_text().strip(),
            "科类名称": page.locator("#enresult1 .klmc").inner_text().strip(),
            "计划性质": page.locator("#enresult1 .jhxzmc").inner_text().strip(),
        }

        return {
            "success": True,
            "admitted": True,
            "data": result
        }

    # 暂无录取
    if page.locator("#enresult2.tab-pane.active").count() > 0:
        return {
            "success": True,
            "admitted": False,
            "message": "暂无录取信息"
        }

    return None


def refresh_captcha(page):
    """
    刷新验证码
    """

    ok_btn = page.locator("div.gbtips")

    if ok_btn.count() > 0 and ok_btn.is_visible():
        ok_btn.click()
        page.wait_for_timeout(500)

    page.locator(".img-verifycode").click()

    page.wait_for_timeout(1500)


def query():
    os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(config.LOGS_DIR, exist_ok=True)

    launch_args = {
        "headless": config.HEADLESS
    }

    if config.BROWSER_PATH:
        launch_args["executable_path"] = config.BROWSER_PATH

    with sync_playwright() as p:

        browser = p.chromium.launch(**launch_args)

        page = browser.new_page()

        page.goto(config.URL)

        page.wait_for_load_state("networkidle")

        # 输入信息
        page.locator("#key1").fill(config.EXAM_NO)

        page.wait_for_timeout(500)

        page.locator("#key2").fill(config.ID_CARD_LAST4)

        page.wait_for_timeout(500)

        for i in range(5):

            # 输入验证码
            page.locator("input.code").fill("")

            code = captcha.get_code(page)

            print(f"第{i + 1}次验证码：{code}")

            page.locator("input.code").fill(code)

            # 点击查询
            page.locator("#btncx").click()

            try:
                # 等待结果tab出现
                page.wait_for_selector(
                    "#enresult1.tab-pane.active,"
                    "#enresult2.tab-pane.active",
                    timeout=5000
                )
                # 打印当前激活的tab
                enresult1_active = page.locator("#enresult1.tab-pane.active").count()
                enresult2_active = page.locator("#enresult2.tab-pane.active").count()

                print("enresult1 active数量：", enresult1_active)
                print("enresult2 active数量：", enresult2_active)

                # 打印页面结果文字
                if enresult1_active > 0:
                    print("检测到：有录取信息")
                    print(
                        page.locator("#enresult1").inner_text()
                    )

                elif enresult2_active > 0:
                    print("检测到：暂无录取信息")
                    print(
                        page.locator("#enresult2").inner_text()
                    )

            except Exception:

                print("验证码错误")

                refresh_captcha(page)

                continue

            result = parse_result(page)

            if result is None:
                write_log("未知查询结果")

                browser.close()

                return False

            # 无录取
            if not result["admitted"]:
                write_log("暂无录取信息")

                browser.close()

                return result

            # 有录取
            write_log(
                f"查询到录取信息：{result['data']}"
            )

            save_screenshot(page)

            browser.close()

            return result

        write_log("连续5次验证码失败")

        browser.close()

        return False
