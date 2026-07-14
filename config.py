from configparser import ConfigParser
import os
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config = ConfigParser()

config_path = os.path.join(BASE_DIR, "config.ini")

if not config.read(config_path, encoding="utf-8"):
    raise FileNotFoundError(f"配置文件不存在：{config_path}")

URL = config.get("system", "url")

EXAM_NO = config.get("system", "exam_no")

ID_CARD_LAST4 = config.get("system", "id_card_last4")

HEADLESS = config.getboolean("system", "headless")

INTERVAL = config.getint("system", "interval")

SCREENSHOT_DIR = config.get("system", "screenshot_dir")

LOGS_DIR = config.get("system", "logs_dir")
BROWSER_PATH = config.get("system", "browser_path", fallback="")