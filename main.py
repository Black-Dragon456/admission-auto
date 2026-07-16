import time
from datetime import datetime, timedelta

import config
from query import query


def main():
    while True:

        now = datetime.now()

        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] 开始查询")

        try:

            result = query(config.EXAM_NO, config.ID_CARD_LAST4)

            print(result)

        except Exception as e:

            print(f"查询异常：{e}")

        next_time = datetime.now() + timedelta(seconds=config.INTERVAL)

        print(
            f"下次执行时间："
            f"{next_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        print("-" * 60)

        time.sleep(config.INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已停止。")
