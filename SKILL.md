# Task Scorekeeper (红绿灯版)

> **红绿灯任务评分员** — 简单直观的任务解决状态追踪

## 核心原则

**简单直接**：红灯停、绿灯行、黄灯等、白灯不计入。

---

## 评分标准

### 🟢 green — 已解决

- 问题已解决，用户确认满意
- 任务完成，预期结果达成

### 🟡 yellow — 待定

- 需要用户进一步确认
- 等待更多信息/环境
- 部分完成，还需后续处理

### 🔴 red — 未解决

- 问题未解决
- 遇到错误/阻塞
- 用户表示不满

### ⚪ white — 不适用

- 非任务对话（问候、寒暄、随便聊聊）
- 无法自动判断的对话
- 不计入解决率统计

---

## 自动触发

Agent 在每次**实质性任务完成**后自动调用。

### 触发信号

| 用户消息信号 | 判定 |
|------------|------|
| 好了/完成/谢谢/done/✅/OK | 🟢 green |
| 不对/重新来/错了/failed | 🔴 red |
| 超时/错误/exception/失败/无法 | 🔴 red |
| 等一下/让我想想/需要确认 | 🟡 yellow |
| 差不多/基本可以 | 🟡 yellow |
| hi/hello/你好/在吗/拜拜 | ⚪ white |
| 随便问问/没事/just checking | ⚪ white |

### 判定优先级

```
1. 错误/失败信号 → 🔴 red
2. 用户纠正信号 → 🔴 red
3. 待定信号     → 🟡 yellow
4. 完成信号     → 🟢 green
5. 非任务对话   → ⚪ white
6. 无法判断     → 不记录（等手动）
```

### API 调用

```python
from skills.task_scorekeeper.traffic_light import TrafficLight

tl = TrafficLight()

# 自动触发（核心方法）
result = tl.auto_trigger(
    user_message='用户最新消息',
    task_output='任务输出',
    error='错误信息',
    task='任务描述',
    conversation_id='当前对话ID'
)
# 返回 None 表示无法自动判断，不记录

# 手动记录白灯
result = tl.rate('white', task='简单问答', note='无法评定的对话', conversation_id='xxx')

# 事后调整
tl.adjust(rating_id=5, new_status='green', note='用户确认已解决')

# 查看统计（白灯不计入解决率）
stats = tl.stats()
print(f"解决率: {stats['resolution_rate']}")
```

---

## CLI 命令速查

| 命令 | 说明 |
|------|------|
| `--status green --task "xxx"` | 记录绿灯 |
| `--status red --reason "xxx"` | 记录红灯 |
| `--status yellow --note "xxx"` | 记录黄灯 |
| `--status white --note "xxx"` | 记录白灯（非任务对话） |
| `--review --days 7` | 查看近7天 |
| `--adjust 5 --new-status green` | 调整历史评定 |
| `--stats` | 统计 |

---

## 数据存储

- **JSON**: `data/traffic_light.json`
- 白灯不计入解决率

### 结构

```json
{
  "ratings": [...],
  "stats": {
    "green": 10,
    "yellow": 2,
    "red": 3,
    "white": 5
  }
}
```

### 解决率计算（不含白灯）

```
解决率 = green / (green + yellow + red) × 100%
```