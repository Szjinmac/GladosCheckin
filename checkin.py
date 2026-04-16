#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLaDOS 自动签到脚本
自动完成每日签到并推送结果通知
"""

import os
import sys
import time
import random
import requests
from typing import Optional, Dict, Any

# 环境变量配置
GLADOS_COOKIE = os.getenv('GLADOS_COOKIE', '')
SERVERCHAN_KEY = os.getenv('SERVERCHAN_KEY', '')
PUSHPLUS_TOKEN = os.getenv('PUSHPLUS_TOKEN', '')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# GLaDOS API 配置
GLADOS_CHECKIN_URL = 'https://glados.cloud/api/user/checkin'
GLADOS_STATUS_URL = 'https://glados.cloud/api/user/status'

# 请求配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'Cookie': GLADOS_COOKIE
}

# 重试配置
MAX_RETRIES = 3
RETRY_INTERVAL = 300  # 5 分钟


class CheckinResult:
    """签到结果"""
    def __init__(self, success: bool, message: str, days: int = 0, balance: int = 0):
        self.success = success
        self.message = message
        self.days = days
        self.balance = balance

    def __str__(self):
        if self.success:
            return f"[签到成功]\n获取积分: {self.days} 天\n总天数: {self.balance} 天"
        else:
            return f"[签到失败]\n错误原因: {self.message}"


def checkin() -> CheckinResult:
    """执行签到操作"""
    if not GLADOS_COOKIE:
        return CheckinResult(False, "未配置 GLADOS_COOKIE 环境变量")

    for attempt in range(MAX_RETRIES):
        try:
            # 发起签到请求
            response = requests.post(
                GLADOS_CHECKIN_URL,
                headers=HEADERS,
                json={'token': 'glados.network'},
                timeout=30
            )

            # 处理响应
            if response.status_code == 200:
                data = response.json()

                # 检查签到结果
                if 'message' in data:
                    message = data.get('message', '')

                    # 已签到情况
                    if '已签到' in message or 'Please try tomorrow' in message or '已经签到' in message:
                        # 尝试获取状态信息
                        try:
                            status_resp = requests.get(GLADOS_STATUS_URL, headers=HEADERS, timeout=10)
                            if status_resp.status_code == 200:
                                status_data = status_resp.json()
                                balance = status_data.get('data', {}).get('balance', 0)
                                return CheckinResult(True, "今日已签到", 0, balance)
                        except:
                            pass
                        return CheckinResult(True, "今日已签到")

                    # 签到成功
                    if data.get('code') == 0 or '成功' in message:
                        days = data.get('list', {}).get('days', 0)
                        balance = data.get('list', {}).get('balance', 0)
                        return CheckinResult(True, message, days, balance)

                    # 其他错误
                    return CheckinResult(False, message)

                return CheckinResult(False, f"未知响应格式: {data}")

            # 认证失败
            elif response.status_code in [401, 403]:
                return CheckinResult(False, "Cookie 已失效，请更新配置")

            # 服务器错误，重试
            else:
                error_msg = f"HTTP {response.status_code}"
                if attempt < MAX_RETRIES - 1:
                    print(f"签到失败 ({error_msg})，{RETRY_INTERVAL}秒后重试 ({attempt + 1}/{MAX_RETRIES})")
                    time.sleep(RETRY_INTERVAL)
                    continue
                return CheckinResult(False, error_msg)

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                print(f"请求超时，{RETRY_INTERVAL}秒后重试 ({attempt + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_INTERVAL)
                continue
            return CheckinResult(False, "网络请求超时")

        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                print(f"网络错误: {e}，{RETRY_INTERVAL}秒后重试 ({attempt + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_INTERVAL)
                continue
            return CheckinResult(False, f"网络错误: {e}")

    return CheckinResult(False, "超过最大重试次数")


def send_serverchan(title: str, content: str) -> bool:
    """发送 Server酱 推送"""
    if not SERVERCHAN_KEY:
        return False

    try:
        url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
        response = requests.post(url, data={'title': title, 'desp': content}, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Server酱推送失败: {e}")
        return False


def send_pushplus(title: str, content: str) -> bool:
    """发送 PushPlus 推送"""
    if not PUSHPLUS_TOKEN:
        return False

    try:
        url = "http://www.pushplus.plus/send"
        response = requests.post(
            url,
            json={'token': PUSHPLUS_TOKEN, 'title': title, 'content': content},
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"PushPlus推送失败: {e}")
        return False


def send_telegram(title: str, content: str) -> bool:
    """发送 Telegram 推送"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        text = f"*{title}*\n\n{content}"
        response = requests.post(
            url,
            json={'chat_id': TELEGRAM_CHAT_ID, 'text': text, 'parse_mode': 'Markdown'},
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram推送失败: {e}")
        return False


def send_notification(result: CheckinResult):
    """发送签到结果通知"""
    title = "GLaDOS 签到成功" if result.success else "GLaDOS 签到失败"
    content = str(result)

    # 尝试所有配置的推送渠道
    channels = []

    if send_serverchan(title, content):
        channels.append("Server酱")

    if send_pushplus(title, content):
        channels.append("PushPlus")

    if send_telegram(title, content):
        channels.append("Telegram")

    if channels:
        print(f"推送通知已发送: {', '.join(channels)}")
    else:
        print("未配置推送服务或推送失败")


def main():
    """主函数"""
    print("=" * 50)
    print("GLaDOS 自动签到服务启动")
    print("=" * 50)

    # 检查配置
    if not GLADOS_COOKIE:
        print("错误: 未配置 GLADOS_COOKIE 环境变量")
        print("请在环境变量中设置 GLADOS_COOKIE")
        sys.exit(1)

    # 执行签到
    print(f"\n开始签到...")
    result = checkin()

    # 输出结果
    print(f"\n{result}")

    # 发送通知
    send_notification(result)

    print("\n" + "=" * 50)
    print("签到任务完成")
    print("=" * 50)

    # 返回退出码
    sys.exit(0 if result.success else 1)


if __name__ == '__main__':
    main()