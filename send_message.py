"""LINE Messaging API でテキスト/画像/スタンプを送るシンプルなスクリプト。"""

from __future__ import annotations

import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

PUSH_API_URL = "https://api.line.me/v2/bot/message/push"


def get_credentials() -> tuple[str, str]:
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.getenv("LINE_USER_ID")

    if not token or not user_id:
        print("LINE_CHANNEL_ACCESS_TOKEN / LINE_USER_ID が未設定です。")
        print(".env ファイルに値を記入してください。")
        sys.exit(1)

    return token, user_id


def send_messages(messages: list[dict]) -> None:
    token, user_id = get_credentials()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {"to": user_id, "messages": messages}

    response = requests.post(PUSH_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        print("メッセージを送信しました")
    else:
        print(f"送信に失敗しました: status={response.status_code}, body={response.text}")


def send_text_message(text: str) -> None:
    send_messages([{"type": "text", "text": text}])


def send_image_message(image_url: str, preview_url: str | None = None) -> None:
    # LINE側が画像を取得できるよう、HTTPSで公開されているJPEG画像のURLを指定する(10MBまで)。
    send_messages(
        [
            {
                "type": "image",
                "originalContentUrl": image_url,
                "previewImageUrl": preview_url or image_url,
            }
        ]
    )


def send_sticker_message(package_id: str, sticker_id: str) -> None:
    # packageId / stickerId は LINE Developers の「スタンプ一覧」で確認できる。
    send_messages(
        [
            {
                "type": "sticker",
                "packageId": package_id,
                "stickerId": sticker_id,
            }
        ]
    )


def print_usage() -> None:
    print("使い方:")
    print('  python send_message.py text "メッセージ"')
    print("  python send_message.py image <画像URL> [プレビューURL]")
    print("  python send_message.py sticker <packageId> <stickerId>")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        send_text_message("テスト送信です")
    elif args[0] == "text":
        send_text_message(args[1] if len(args) > 1 else "テスト送信です")
    elif args[0] == "image":
        if len(args) < 2:
            print_usage()
            sys.exit(1)
        send_image_message(args[1], args[2] if len(args) > 2 else None)
    elif args[0] == "sticker":
        if len(args) < 3:
            print_usage()
            sys.exit(1)
        send_sticker_message(args[1], args[2])
    else:
        # サブコマンド省略時は従来通りテキストとして扱う
        send_text_message(args[0])
