import base64
import time

import ddddocr


ocr = ddddocr.DdddOcr(show_ad=False)


def get_code(session):
    """
    获取验证码并OCR识别
    """

    url = f"https://jxcf.jxeea.cn/captcha/getcode?t={int(time.time() * 1000)}"

    response = session.get(url, timeout=10)

    response.raise_for_status()

    data = response.json()

    if data.get("Code") != 1:
        raise RuntimeError("获取验证码失败")

    img_base64 = data["Data"]["Img"]

    image = base64.b64decode(img_base64)

    code = ocr.classification(image).strip()

    print(f"验证码：{code}")

    return code