import os
import sys
import time
from datetime import datetime, timedelta

import config
from query import query


# 切换到程序所在目录（兼容 PyInstaller）
def init():
    if getattr(sys, "frozen", False):
        # exe运行
        base_dir = os.path.dirname(sys.executable)
    else:
        # py运行
        base_dir = os.path.dirname(os.path.abspath(__file__))

    os.chdir(base_dir)

    # 创建目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)


def write_log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

    with open("logs/query.log", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {msg}\n")


def main():
    while True:
        try:
            write_log("开始查询")

            query()

            next_time = datetime.now() + timedelta(seconds=config.INTERVAL)
            write_log(f"下次执行时间：{next_time.strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            write_log(f"查询异常：{e}")

        time.sleep(config.INTERVAL)


if __name__ == "__main__":
    init()

    try:
        main()
    except KeyboardInterrupt:
        write_log("程序已停止")