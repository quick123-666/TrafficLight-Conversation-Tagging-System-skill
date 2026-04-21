#!/usr/bin/env python3
# Windows console UTF-8 fix
import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""
Traffic Light Task Scorekeeper - 红绿灯任务评分员

简单评定：
- 🟢 green: 问题已解决
- 🔴 red: 问题未解决
- 🟡 yellow: 待定/等待处理

支持事后追加评定 - 后续对话可以更新之前的评分

使用:
  python traffic_light.py --status green --task "修复bug"
  python traffic_light.py --status red --reason "需要更多信息"
  python traffic_light.py --review --days 7
  python traffic_light.py --adjust 3 --status green --note "用户确认已解决"
"""

import json, os, sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class TrafficLight:
    """红绿灯任务评分器"""
    
    STATUS_MAP = {
        'green': {'emoji': '🟢', 'name': '已解决', 'color': '#4CAF50'},
        'yellow': {'emoji': '🟡', 'name': '待定', 'color': '#FFC107'},
        'red': {'emoji': '🔴', 'name': '未解决', 'color': '#F44336'},
        'white': {'emoji': '⚪', 'name': '不适用', 'color': '#9E9E9E'},
    }
    
    def __init__(self, log_path: str = None):
        if log_path is None:
            base = Path(os.environ.get('ASSISTANT_ROOT', 
                r'C:\Users\Administrator\assistants\assistant-1'))
            log_path = base / 'data' / 'traffic_light.json'
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._load()
    
    def _load(self):
        if self.log_path.exists():
            with open(self.log_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            # 确保有 white 键（兼容旧数据）
            if 'white' not in self.data.get('stats', {}):
                self.data.setdefault('stats', {})
                self.data['stats']['white'] = 0
        else:
            self.data = {'ratings': [], 'stats': {'green': 0, 'yellow': 0, 'red': 0, 'white': 0}}
    
    def _save(self):
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def _update_stats(self):
        stats = {'green': 0, 'yellow': 0, 'red': 0, 'white': 0}
        for r in self.data['ratings']:
            if r['status'] in stats:
                stats[r['status']] += 1
        self.data['stats'] = stats
    
    def rate(self, status: str, task: str = '', note: str = '', 
             conversation_id: str = '', auto: bool = False) -> dict:
        """
        评定任务状态
        
        Args:
            status: green | yellow | red
            task: 任务描述
            note: 备注/原因
            conversation_id: 对话ID（用于关联）
            auto: 是否自动触发
        """
        if status not in self.STATUS_MAP:
            return {'error': f'无效状态: {status}'}
        
        entry = {
            'id': len(self.data['ratings']) + 1,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'status': status,
            'emoji': self.STATUS_MAP[status]['emoji'],
            'task': task,
            'note': note,
            'conversation_id': conversation_id,
            'auto': auto,
            'updated_at': None,
            'history': []  # 记录修改历史
        }
        
        self.data['ratings'].append(entry)
        self._update_stats()
        self._save()
        
        return entry
    
    def adjust(self, rating_id: int, new_status: str, note: str = '') -> dict:
        """
        调整历史评定 - 支持事后追加评定
        
        Args:
            rating_id: 评定期ID
            new_status: 新状态
            note: 追加说明
        """
        for entry in self.data['ratings']:
            if entry['id'] == rating_id:
                old_status = entry['status']
                old_emoji = entry['emoji']
                
                # 记录历史
                entry['history'].append({
                    'from': old_status,
                    'to': new_status,
                    'at': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'note': note
                })
                
                # 更新状态
                entry['status'] = new_status
                entry['emoji'] = self.STATUS_MAP[new_status]['emoji']
                entry['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                
                if note:
                    entry['note'] = f"{entry['note']} [+调整: {note}]" if entry['note'] else note
                
                self._update_stats()
                self._save()
                
                return {
                    'id': rating_id,
                    'old': f'{old_emoji} {old_status}',
                    'new': f'{self.STATUS_MAP[new_status]["emoji"]} {new_status}',
                    'entry': entry
                }
        
        return {'error': f'未找到 ID={rating_id} 的评定'}
    
    def review(self, days: int = 7, status: str = None) -> list:
        """查看近期评定"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        results = []
        for r in self.data['ratings']:
            dt = datetime.strptime(r['timestamp'], '%Y-%m-%d %H:%M')
            if dt >= cutoff:
                if status is None or r['status'] == status:
                    results.append(r)
        return results
    
    def stats(self) -> dict:
        """统计（白灯不计入解决率）"""
        total = sum(self.data['stats'].values())
        # 解决率 = green / (green + yellow + red)
        rated = self.data['stats']['green'] + self.data['stats']['yellow'] + self.data['stats']['red']
        return {
            **self.data['stats'],
            'total': total,
            'resolution_rate': f"{self.data['stats']['green'] / rated * 100:.1f}%" if rated > 0 else "N/A",
            'note': 'resolution excludes white (N/A conversations)'
        }
    
    def get_by_conversation(self, conversation_id: str) -> list:
        """获取指定对话的所有评定"""
        return [r for r in self.data['ratings'] 
                if r.get('conversation_id') == conversation_id]

    def auto_trigger(self, user_message: str = '', task_output: str = '',
                     error: str = '', task: str = '',
                     conversation_id: str = '') -> Optional[dict]:
        """
        根据上下文自动判断并触发评分
        
        Args:
            user_message: 用户最新消息
            task_output: 任务输出结果
            error: 错误信息
            task: 任务描述（从上下文中提取）
            conversation_id: 对话ID
        
        Returns:
            评分结果 dict，如果无法自动判断则返回 None
        """
        um = (user_message or '').lower()
        out = (task_output or '').lower()
        err = (error or '').lower()

        # ── 🔴 失败信号 ──
        fail_signals = [
            'error', 'failed', 'timeout', 'exception', '超时',
            'not found', 'permission denied', 'exit code 1',
            'traceback', 'no such', 'unauthorized',
            'connection refused', 'could not', 'refused', '无法',
            '不对', '错了', '重新来', '不行', '没解决', '失败'
        ]
        if any(s in err or s in um for s in fail_signals):
            return self.rate('red', task=task, note=f'失败: {error[:80]}' if error else '命令/操作失败',
                             conversation_id=conversation_id, auto=True)

        # ── 用户纠正 ──
        correction_signals = [
            'no,', 'not right', 'wrong', 'should be', 'incorrect',
            'don\'t do that', 'stop', 'that\'s wrong',
            '重新', '错了', '不对', '不是这样', '等等'
        ]
        if any(s in um for s in correction_signals):
            return self.rate('red', task=task, note=f'用户纠正: {user_message[:80]}',
                             conversation_id=conversation_id, auto=True)

        # ── 🟡 待定信号 ──
        pending_signals = [
            '等一下', '等会', '稍等', '等一下',
            '我看看', '让我想想', '需要确认',
            'wait', 'hold on', 'need to check',
            '不确定', '问一下', '再说'
        ]
        if any(s in um for s in pending_signals):
            return self.rate('yellow', task=task, note=f'待定: {user_message[:80]}',
                             conversation_id=conversation_id, auto=True)

        # ── 🟢 成功信号 ──
        success_signals = [
            '好了', '完成了', '成功了', '搞定', '可以了',
            '谢谢', '谢谢！', 'ok', 'okay', 'perfect', 'great',
            '✅', '👍', '对了', '没问题', '已解决',
            'done', 'done!', 'solved', 'fixed', 'works',
            '搞定！', '好的', '好'
        ]
        if any(s in um for s in success_signals):
            return self.rate('green', task=task, note=f'完成: {user_message[:80]}',
                             conversation_id=conversation_id, auto=True)

        # ── 部分完成 ──
        partial_signals = ['差不多了', '基本可以', '大致完成', '部分完成']
        if any(s in um for s in partial_signals):
            return self.rate('yellow', task=task, note=f'部分完成: {user_message[:80]}',
                             conversation_id=conversation_id, auto=True)

        # ── 白灯：不适用（非任务对话） ──
        # 到这里说明没有任何匹配
        non_task_signals = [
            'hi', 'hello', '嗨', '你好', '早上好', '下午好', '晚上好',
            '在吗', '？', '?', 'help', 'just checking', '没事', '随便问问',
            'thanks for', 'bye', '再见', '拜拜'
        ]
        # 非任务对话 → 白灯
        if any(s in um for s in non_task_signals):
            return self.rate('white', task=task, note=f'非任务对话: {user_message[:80]}',
                             conversation_id=conversation_id, auto=True)
        # 其他无法自动判断的实质性任务 → 不记录（等用户手动）
        return None

        return result


# ── CLI 入口 ────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Traffic Light Task Scorekeeper')
    
    parser.add_argument('--status', choices=['green', 'yellow', 'red', 'white'],
                        help='评定状态')
    parser.add_argument('--task', default='', help='任务描述')
    parser.add_argument('--note', default='', help='备注/原因')
    parser.add_argument('--conversation', default='', help='对话ID')
    parser.add_argument('--auto', action='store_true', help='自动触发')
    
    parser.add_argument('--adjust', type=int, help='调整指定ID的评定')
    parser.add_argument('--new-status', dest='new_status',
                        choices=['green', 'yellow', 'red', 'white'], help='新状态')
    parser.add_argument('--adjust-note', dest='adjust_note', default='', help='调整备注')
    
    parser.add_argument('--review', action='store_true', help='查看近期评定')
    parser.add_argument('--days', type=int, default=7, help='查看天数')
    parser.add_argument('--filter-status', dest='filter_status',
                        choices=['green', 'yellow', 'red', 'white'], help='按状态筛选')
    
    parser.add_argument('--stats', action='store_true', help='查看统计')
    
    args = parser.parse_args()
    tl = TrafficLight()
    
    # 调整历史评定
    if args.adjust:
        if not args.new_status:
            print('❌ 需要 --new-status 参数')
            return
        result = tl.adjust(args.adjust, args.new_status, args.adjust_note)
        if 'error' in result:
            print(f"❌ {result['error']}")
        else:
            print(f"✅ 调整: {result['old']} → {result['new']}")
        return
    
    # 新评定
    if args.status:
        result = tl.rate(args.status, args.task, args.note, args.conversation, args.auto)
        emoji = tl.STATUS_MAP[args.status]['emoji']
        print(f"{emoji} 评定已记录: {args.status}")
        print(f"   任务: {args.task or '(无描述)'}")
        if args.note:
            print(f"   备注: {args.note}")
        return
    
    # 统计
    if args.stats:
        s = tl.stats()
        print(f"\n📊 四色灯统计 (近 {args.days} 天)")
        print(f"  🟢 已解决: {s['green']}")
        print(f"  🟡 待定:   {s['yellow']}")
        print(f"  🔴 未解决: {s['red']}")
        print(f"  ⚪ 不适用: {s['white']}")
        print(f"  ──────────────────")
        print(f"  总计:     {s['total']}")
        print(f"  解决率:   {s['resolution_rate']}  (不含白灯)")
        return
    
    # 查看近期
    if args.review:
        recent = tl.review(args.days, args.filter_status)
        if not recent:
            print(f'📋 近 {args.days} 天无评定记录')
            return
        print(f"\n📋 近 {args.days} 天评定 ({len(recent)} 条):\n")
        for r in recent:
            print(f"  {r['emoji']} #{r['id']} {r['timestamp']} [{r['status']}]")
            if r.get('task'):
                print(f"      任务: {r['task'][:50]}")
            if r.get('note'):
                print(f"      备注: {r['note'][:50]}")
            if r.get('history'):
                print(f"      📜 有 {len(r['history'])} 次历史调整")
        return
    
    parser.print_help()


if __name__ == '__main__':
    main()
