import json
import os
from datetime import datetime

import requests
from lzstring import LZString

import captcha
import config
import parser

lz = LZString()


def compress(text: str) -> str:
    """
    与网页 LZString.compressToBase64() 保持一致
    """
    return lz.compressToBase64(text)


def write_query_log(message: str):
    """
    写查询日志
    """
    os.makedirs(config.LOGS_DIR, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(
            os.path.join(config.LOGS_DIR, "query.log"),
            "a",
            encoding="utf-8"
    ) as f:
        f.write(f"[{now}] {message}\n")

def write_result_log(result: dict):
    """
    写查询结果日志
    """
    os.makedirs(config.LOGS_DIR, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(
            os.path.join(config.LOGS_DIR, "result.log"),
            "a",
            encoding="utf-8"
    ) as f:
        f.write(f"[{now}] {json.dumps(result, ensure_ascii=False, indent=4)}")
        f.write("\n")


def create_session() -> requests.Session:
    """
    创建Session
    """
    session = requests.Session()

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/150.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": config.URL + "/",
        "Origin": config.URL,
    })

    return session


def query():
    """
    查询录取结果
    """

    session = create_session()

    # 先访问首页，建立Cookie
    home = session.get(config.URL, timeout=10)
    home.raise_for_status()


    # OCR 最多识别5次
    for i in range(5):

        try:

            # 获取验证码
            code = captcha.get_code(session)

            print(f"第{i + 1}次验证码：{code}")

            write_query_log(f"第{i + 1}次验证码：{code}")

            form = {
                "key1": compress(config.EXAM_NO),
                "key2": compress(config.ID_CARD_LAST4),
                "key3": compress(code)
            }

            response = session.post(
                config.URL,
                data=form,
                timeout=10
            )

            response.raise_for_status()

            # 调试：保存POST返回页面
            #with open("post_result.html", "w", encoding="utf-8") as f:
                #f.write(response.text)

            result = parser.parse(response.text)
            if not result["success"]:
                write_query_log(result.get("message", "查询失败"))
                continue
            # 查询成功
            if result["admitted"]:
                admission = result["admission"]

                write_query_log(
                    "查询成功：已录取 | "
                    f"院校：{admission['院校名称']} | "
                    f"专业：{admission['专业名称']} | "
                    f"批次：{admission['批次名称']} | "
                    f"状态：{admission['考生状态']}"
                )
            else:
                write_query_log("查询成功：暂无录取信息")
            write_result_log(result)
            return result
        except Exception as e:

            write_query_log(f"第{i + 1}次查询异常：{e}")

            print(e)

    write_query_log("连续5次验证码识别失败")

    return {
        "success": False,
        "message": "连续5次验证码识别失败"
    }