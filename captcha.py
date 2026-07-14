import base64
import ddddocr

ocr = ddddocr.DdddOcr(show_ad=False)


def get_code(page):
    """
    获取验证码
    """

    src = page.locator(".img-verifycode").get_attribute("src")

    base64_str = src.split(",")[1]

    img = base64.b64decode(base64_str)

    code = ocr.classification(img)

    print("验证码：", code)

    return code