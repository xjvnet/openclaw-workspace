#!/usr/bin/env python3
"""
股票预警脚本 - 优化版，直接调用腾讯接口
"""
import requests
import json
import os
from datetime import datetime

# ========== 配置 ==========
ALERTS = [
    {"code": "002734", "name": "利民股份", "condition": "above", "price": 25.8},
]

STATE_FILE = "/root/.openclaw/workspace/.stock_alert_state.json"
# ==========================

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def get_stock_price(code):
    """通过腾讯接口获取实时股价"""
    try:
        # 格式化代码
        if code.startswith('6'):  # 上海
            full_code = f"sh{code}"
        else:  # 深圳
            full_code = f"sz{code}"
        
        url = f"https://qt.gtimg.cn/q={full_code}"
        resp = requests.get(url, timeout=10)
        resp.encoding = 'gbk'
        
        # 解析返回数据: v_sh002734="1~利民股份~...~当前价~..."
        data = resp.text.strip()
        if not data or '~' not in data:
            return None
        
        parts = data.split('~')
        if len(parts) >= 4:
            return float(parts[3])  # 当前价在第4个位置
    except Exception as e:
        print(f"获取 {code} 失败: {e}")
    return None

def check_alerts():
    state = load_state()
    triggered = []
    
    for alert in ALERTS:
        code = alert['code']
        name = alert['name']
        price = get_stock_price(code)
        
        if price is None:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {name}({code}) 查询失败")
            continue
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {name}({code}): ¥{price}")
        
        condition_met = False
        alert_key = f"{code}_{alert['condition']}_{alert['price']}"
        
        if alert['condition'] == 'below' and price < alert['price']:
            condition_met = True
            msg = f"🚨 {name}({code}) 跌破 ¥{alert['price']}，当前 ¥{price}"
        elif alert['condition'] == 'above' and price > alert['price']:
            condition_met = True
            msg = f"🚨 {name}({code}) 突破 ¥{alert['price']}，当前 ¥{price}"
        
        # 避免重复报警（同一天内只报一次）
        today = datetime.now().strftime('%Y-%m-%d')
        if condition_met and state.get(alert_key) != today:
            triggered.append(msg)
            state[alert_key] = today
            print(f"⚠️ 触发预警: {msg}")
    
    save_state(state)
    return triggered

def is_trading_time():
    """检查是否是A股交易时间（周一到周五，9:30-11:30, 13:00-15:00）北京时间"""
    import pytz
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    weekday = now.weekday()  # 0-6 (周一到周日)
    hour = now.hour
    minute = now.minute
    time_val = hour * 100 + minute  # 如 930 表示 9:30
    
    # 周一到周五 (0-4)
    if weekday > 4:
        return False
    
    # 上午 9:30-11:30 或 下午 13:00-15:00
    if (930 <= time_val <= 1130) or (1300 <= time_val <= 1500):
        return True
    
    return False

if __name__ == "__main__":
    # 检查是否是交易时间
    if not is_trading_time():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 非A股交易时间，跳过检查")
        exit(0)
    
    alerts = check_alerts()
    for msg in alerts:
        print(msg)
