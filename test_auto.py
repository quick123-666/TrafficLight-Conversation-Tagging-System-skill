#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from traffic_light import TrafficLight

tl = TrafficLight()

tests = [
    ('好了，完成了', 'green'),
    ('谢谢，问题解决了', 'green'),
    ('不对，应该这样', 'red'),
    ('等一下，我看看', 'yellow'),
    ('失败了，timeout', 'red'),
    ('让我想想', 'yellow'),
    ('done', 'green'),
    ('不对，重新来', 'red'),
    ('连接超时了', 'red'),
]

print("=== Auto Trigger Tests ===")
all_ok = True
for msg, expected in tests:
    result = tl.auto_trigger(user_message=msg, task='test', conversation_id='test')
    status = result['status'] if result else 'N/A'
    ok = 'OK' if status == expected else 'FAIL'
    if status != expected:
        all_ok = False
    print(f"[{ok}] '{msg}' -> {status} (expected {expected})")

import json
data_path = os.path.join(os.environ.get('ASSISTANT_ROOT', 
    r'C:\Users\Administrator\assistants\assistant-1'), 'data', 'traffic_light.json')
with open(data_path, encoding='utf-8') as f:
    data = json.load(f)
print(f"\nTotal: {len(data['ratings'])}, stats: {data['stats']}")
print('All passed!' if all_ok else 'Some failed.')