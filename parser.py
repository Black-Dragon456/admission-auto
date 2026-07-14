import json
import re



def _extract_json(html: str, var_name: str):
    """
    提取页面中的 JS 变量

    var _score = '...'.toLowerCase();
    var _luqu = '...';

    返回 dict 或 None
    """

    # 带 .toLowerCase()
    pattern1 = rf"var\s+{var_name}\s*=\s*'(.*?)'\.toLowerCase\(\);"

    # 不带 .toLowerCase()
    pattern2 = rf"var\s+{var_name}\s*=\s*'(.*?)';"

    match = re.search(pattern1, html, re.S)

    if not match:
        match = re.search(pattern2, html, re.S)

    if not match:
        return None

    text = match.group(1).strip()

    if not text:
        return None

    try:
        return json.loads(text)
    except Exception:
        return None


def parse(html: str):
    """
    解析查询结果
    """

    score = _extract_json(html, "_score")
    luqu = _extract_json(html, "_luqu")

    # 页面异常
    if score is None:
        return {
            "success": False,
            "message": "查询失败，未获取到成绩数据"
        }

    result = {
        "success": True
    }

    # =========================
    # 先解析录取信息
    # =========================
    if luqu is not None:
        result["admitted"] = True
        result["message"] = "已查询到录取信息"

        result["admission"] = {
            "考生状态": luqu.get("LQZTMC", "").strip(),
            "院校代号": luqu.get("YXDH", "").strip(),
            "院校名称": luqu.get("YXMC", "").strip(),
            "专业组名称": luqu.get("ZYZMC", "").strip(),
            "专业代号": luqu.get("ZYDH", "").strip(),
            "专业名称": luqu.get("ZYMC", "").strip(),
            "批次名称": luqu.get("PCMC", "").strip(),
            "科类名称": luqu.get("KLMC", "").strip(),
            "计划性质": luqu.get("JHXZMC", "").strip(),
        }
    else:
        result["admitted"] = False
        result["message"] = "暂无录取信息"
        result["admission"] = None

    # =========================
    # 最后解析成绩
    # =========================
    result["score"] = {
        "姓名": score.get("XM", "").strip(),
        "准考证号": score.get("ZKZH", "").strip(),
        "考生号": score.get("KSH", "").strip(),
        "语文": score.get("YW", "").strip(),
        "数学": score.get("SX", "").strip(),
        "外语": score.get("WY", "").strip(),
        score.get("SXKMMC", "").strip(): score.get("SXKM", "").strip(),
        score.get("ZXKM1MC", "").strip(): score.get("ZXKM1", "").strip(),
        score.get("ZXKM2MC", "").strip(): score.get("ZXKM2", "").strip(),
        "总分": score.get("TZF", "").strip(),
        "排名": score.get("PM", "").strip(),
    }

    return result
