#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from traffic_light import TrafficLight

tl = TrafficLight()

tests = [
    # 标准信号
    ('好了，完成了', 'green'),
    ('不对，重新来', 'red'),
    ('等一下，让我看看', 'yellow'),
    # 白灯测试 - 非任务对话
    ('hi', 'white'),
    ('你好', 'white'),
    ('再见', 'white'),
    ('在吗？', 'white'),
    ('没事，随便问问', 'white'),
    ('just checking in', 'white'),
]

print("=== 4色灯测试 ===")
all_ok = True
for msg, expected in tests:
    result = tl.auto_trigger(user_message=msg, task='测试', conversation_id='test-white')
    status = result['status'] if result else 'N/A'
    ok = 'OK' if status == expected else 'FAIL'
    if status != expected:
        all_ok = False
    print(f"[{ok}] '{msg}' -> {status} (expected {expected})")

print()
print('=== 统计 ===')
stats = tl.stats()
total_rated = stats['green'] + stats['yellow'] + stats['red']
resolution = f"{stats['green'] / total_rated * 100:.1f}%" if total_rated > 0 else "N/A"
print(f"  stats: {stats}")
print(f"  解决率(不含白灯): {resolution}")
print(f"\n{'All passed!' if all_ok else 'Some failed.'}")