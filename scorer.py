#!/usr/bin/env python3
"""
Task Scorekeeper - 任务评分核心脚本
"""
import json, os, sys, re, textwrap
from datetime import datetime

# Windows console UTF-8 fix
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE  = os.path.join(SKILL_DIR, "score_log.md")
STATS_FILE = os.path.join(SKILL_DIR, "stats.json")
CRITERIA_FILE = os.path.join(SKILL_DIR, "criteria.md")

# ── 评分标准（可动态更新）─────────────────────────────────────────────────────
DEFAULT_CRITERIA = """
## 评分标准 v1.0

### 结果定义

| 结果 | 标识 | 条件 |
|------|------|------|
| 成功 | ✅ | 目标完全达成，无明显问题 |
| 部分成功 | ⚠️ | 达成部分目标，或有改进空间，或多次尝试才成功 |
| 失败 | ❌ | 目标未达成，或出现严重错误，或违反安全原则 |

### 类型参考

- **coding**：写代码、调试、代码审查
- **research**：搜索、调研、信息整理
- **writing**：文档、报告、文案撰写
- **automation**：自动化操作、批量处理
- **config**：配置、环境搭建、系统设置
- **other**：不属于以上类型

### 加分项（成功率外参考）
- 发现更优方案并推荐
- 主动识别遗漏步骤
- 完成后提供后续建议

### 扣分项
- 跳过必要步骤（自检、确认）
- 重复犯同一个错误
- 未记录值得注意的教训
"""

TASK_TYPES = ["coding", "research", "writing", "automation", "config", "other"]
OUTCOMES   = ["success", "partial", "failure"]
OUTCOME_EMOJI = {"success": "✅", "partial": "⚠️", "failure": "❌"}

# ── 工具函数 ────────────────────────────────────────────────────────────────

def _load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "total": 0,
        "success": 0,
        "partial": 0,
        "failure": 0,
        "by_type": {t: {"total": 0, "success": 0} for t in TASK_TYPES},
        "log_version": 1,
        "last_updated": ""
    }

def _save_stats(stats):
    stats["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def _read_log_tail(n=5):
    """读取日志最后 n 条（不含头部）"""
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, encoding="utf-8") as f:
        lines = f.readlines()
    entries = []
    current = []
    for line in lines:
        if line.startswith("## 20") and current:
            entries.append("".join(current))
            current = []
        current.append(line)
    if current:
        entries.append("".join(current))
    return entries[-n:] if len(entries) >= n else entries

def _next_number():
    """获取下一个任务序号"""
    stats = _load_stats()
    return stats.get("total", 0) + 1

# ── 核心 API ─────────────────────────────────────────────────────────────────

def score_task(
    task_name: str,
    outcome: str = "success",
    task_type: str = "other",
    notes: str = "",
    tags: str = "",
    auto: bool = False
) -> dict:
    """
    记录一次任务评分。

    参数:
        task_name: 任务描述（简短）
        outcome:   success | partial | failure
        task_type: coding | research | writing | automation | config | other
        notes:     评分原因/说明
        tags:      逗号分隔标签
        auto:      True=自动判断（扫描是否有错误信息）

    返回:
        评分结果摘要 dict
    """
    outcome = outcome.lower().strip()
    task_type = task_type.lower().strip()

    if outcome not in OUTCOMES:
        print(f"[WARN] Unknown outcome '{outcome}', defaulting to 'partial'")
        outcome = "partial"
    if task_type not in TASK_TYPES:
        print(f"[WARN] Unknown task_type '{task_type}', defaulting to 'other'")
        task_type = "other"

    now = datetime.now()
    ts  = now.strftime("%Y-%m-%d %H:%M")
    num = _next_number()
    emoji = OUTCOME_EMOJI[outcome]

    # ── 写入日志 ──
    header = f"## {ts} | #{num} | {task_type.upper()} | {emoji} | {task_name}\n"
    body   = textwrap.dedent(f"""\
        **任务：** {task_name}
        **类型：** {task_type}
        **结果：** {emoji} {'成功' if outcome=='success' else '部分成功' if outcome=='partial' else '失败'}
        **说明：** {notes or '（无）'}
        **Tags：** {tags or '（无）'}

        ---
        """) + "\n"

    init_header = ""
    if not os.path.exists(LOG_FILE):
        init_header = "# 任务评分日志\n\n"
    elif os.path.getsize(LOG_FILE) == 0:
        init_header = "# 任务评分日志\n\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        if init_header:
            f.write(init_header)
        f.write(header)
        f.write(body)

    # ── 更新统计 ──
    stats = _load_stats()
    stats["total"] += 1
    stats[outcome]  = stats.get(outcome, 0) + 1
    if task_type in stats["by_type"]:
        stats["by_type"][task_type]["total"]   += 1
        if outcome == "success":
            stats["by_type"][task_type]["success"] += 1
    _save_stats(stats)

    result = {
        "num":      num,
        "task":     task_name,
        "outcome":  outcome,
        "emoji":    emoji,
        "type":     task_type,
        "notes":    notes,
        "stats": {
            "total":   stats["total"],
            "success_rate": f"{_success_rate(stats):.1f}%"
        }
    }
    _print_result(result)
    return result

def _success_rate(stats):
    t = stats["total"]
    if t == 0: return 0.0
    return stats.get("success", 0) / t * 100

def _print_result(r):
    print(f"\n{'='*50}")
    print(f"  📋 任务 #{r['num']} 评分完成")
    print(f"{'='*50}")
    print(f"  任务：{r['task']}")
    print(f"  类型：{r['type']}")
    print(f"  结果：{r['emoji']} {'成功' if r['outcome']=='success' else '部分成功' if r['outcome']=='partial' else '失败'}")
    if r['notes']:
        print(f"  说明：{r['notes']}")
    print(f"  ─────────────────────────────────")
    print(f"  历史累计：共 {r['stats']['total']} 任务，成功率 {r['stats']['success_rate']}")
    print(f"{'='*50}\n")

def get_stats() -> dict:
    """返回评分统计摘要"""
    stats = _load_stats()
    sr = _success_rate(stats)
    by_type = {}
    for t, d in stats.get("by_type", {}).items():
        rt = d["total"]
        rs = d.get("success", 0)
        by_type[t] = {
            "total":      rt,
            "success":    rs,
            "rate":       f"{rs/rt*100:.1f}%" if rt > 0 else "N/A"
        }
    return {
        "total":        stats["total"],
        "success":      stats.get("success", 0),
        "partial":      stats.get("partial", 0),
        "failure":      stats.get("failure", 0),
        "success_rate": f"{sr:.1f}%",
        "by_type":      by_type,
        "last_updated": stats.get("last_updated", "never")
    }

def show_stats():
    """打印格式化的统计报表"""
    s = get_stats()
    print(f"\n📊 任务评分统计（截至 {s['last_updated']}）")
    print("─" * 45)
    print(f"  总任务数  ：{s['total']}")
    print(f"  ✅ 成功  ：{s['success']}  ({s['success_rate']})")
    print(f"  ⚠️ 部分  ：{s['partial']}")
    print(f"  ❌ 失败  ：{s['failure']}")
    print("\n  按类型分布：")
    for t, d in s["by_type"].items():
        if d["total"] > 0:
            print(f"    [{t:12}] {d['total']} 任务，成功率 {d['rate']}")
    print("─" * 45)

def get_log(n=10) -> list:
    """返回最近 n 条评分记录"""
    entries = _read_log_tail(n)
    if not entries:
        print("（暂无评分记录）")
        return []
    print(f"\n📋 最近 {len(entries)} 条评分记录：\n")
    for e in entries:
        print(e)
    return entries

def update_criteria(new_rules: str):
    """更新评分标准文档"""
    with open(CRITERIA_FILE, "w", encoding="utf-8") as f:
        f.write("# 评分标准\n\n")
        f.write(new_rules.strip() + "\n")
    print(f"[OK] 评分标准已更新 → {CRITERIA_FILE}")

# ── CLI 入口 ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Task Scorekeeper CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_score  = sub.add_parser("score",  help="记录一次评分")
    p_score.add_argument("--name",   required=True, help="任务名称")
    p_score.add_argument("--type",   default="other", help="任务类型")
    p_score.add_argument("--outcome",default="success", help="结果: success/partial/failure")
    p_score.add_argument("--notes",  default="", help="说明")
    p_score.add_argument("--tags",   default="", help="标签（逗号分隔）")

    sub.add_parser("stats",  help="查看统计")
    sub.add_parser("log",    help="查看评分日志").add_argument("-n", default=10, type=int)
    sub.add_parser("init",   help="初始化日志文件")

    args = parser.parse_args()

    if args.cmd == "score":
        score_task(args.name, args.outcome, args.type, args.notes, args.tags)
    elif args.cmd == "stats":
        show_stats()
    elif args.cmd == "log":
        get_log(args.n)
    elif args.cmd == "init":
        os.makedirs(SKILL_DIR, exist_ok=True)
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("# 任务评分日志\n\n")
        print(f"[OK] 日志文件已初始化 → {LOG_FILE}")
    else:
        parser.print_help()
