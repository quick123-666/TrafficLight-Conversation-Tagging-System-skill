# Traffic Light Conversation Tagging System

![GitHub](https://img.shields.io/github/license/quick123-666/TrafficLight-Conversation-Tagging-System-skill)
![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![GitHub last commit](https://img.shields.io/github/last-commit/quick123-666/TrafficLight-Conversation-Tagging-System-skill)
![GitHub issues](https://img.shields.io/github/issues/quick123-666/TrafficLight-Conversation-Tagging-System-skill)

🚦 **四色灯对话标记系统** - 用于AI助手任务自动评分的智能工具

一个基于红绿灯（🟢🟡🔴⚪）概念的任务评分系统，帮助AI助手自动评估任务完成状态，提供直观的解决率统计和任务追踪。

## 📋 目录

- [关于项目](#关于项目)
- [功能特性](#功能特性)
- [快速开始](#快速开始)
  - [前提条件](#前提条件)
  - [安装](#安装)
  - [使用](#使用)
- [使用示例](#使用示例)
- [项目结构](#项目结构)
- [贡献指南](#贡献指南)
- [许可证](#许可证)
- [联系方式](#联系方式)
- [致谢](#致谢)

## 🎯 关于项目

**Traffic Light Conversation Tagging System** 是一个专门为AI助手设计的任务评分系统。它基于简单的红绿灯概念，自动评估每次对话任务的完成状态：

- 🟢 **绿灯** - 任务已解决（用户确认满意）
- 🟡 **黄灯** - 待定（需要用户确认/等待信息）
- 🔴 **红灯** - 未解决（命令失败/用户纠正）
- ⚪ **白灯** - 不适用（非任务对话）

### 为什么需要这个系统？

在AI助手的工作中，准确评估任务完成状态至关重要。这个系统帮助：
- **自动评分**：根据对话内容自动判断任务状态
- **解决率统计**：追踪任务完成率和改进空间
- **历史记录**：保存所有评分记录，支持事后调整
- **质量监控**：为AI助手性能提供量化指标

## ✨ 功能特性

### 🚦 四色灯评分
- **智能判断**：基于用户消息自动触发评分
- **状态明确**：四种状态清晰标识任务进展
- **事后调整**：支持历史评分修改和更新

### 📊 统计分析
- **解决率计算**：自动计算任务解决率（不含白灯）
- **趋势分析**：查看近期评分趋势和模式
- **数据导出**：JSON格式存储，便于分析

### 🔧 技术特性
- **Python实现**：纯Python编写，跨平台兼容
- **简单API**：易于集成到现有AI助手系统
- **配置灵活**：支持自定义评分规则和阈值
- **错误处理**：完善的异常处理和日志记录

## 🚀 快速开始

### 前提条件

- Python 3.8 或更高版本
- Git（用于克隆仓库）

### 安装

1. **克隆仓库**
   ```bash
   git clone https://github.com/quick123-666/TrafficLight-Conversation-Tagging-System-skill.git
   cd TrafficLight-Conversation-Tagging-System-skill
   ```

2. **（可选）创建虚拟环境**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **无需额外依赖**
   ```bash
   # 系统已包含所有必要库
   # 只需确保Python环境可用
   ```

### 使用

#### 基本使用

```python
from traffic_light import TrafficLight

# 初始化评分器
tl = TrafficLight()

# 自动触发评分
result = tl.auto_trigger(
    user_message="好了，完成了",
    task_output="任务执行成功",
    error="",
    task="测试任务",
    conversation_id="test_123"
)

print(f"评分结果: {result['emoji']} {result['status']}")
```

#### 命令行使用

```bash
# 记录绿灯（任务完成）
python traffic_light.py --status green --task "修复bug" --note "用户确认已解决"

# 记录红灯（任务失败）
python traffic_light.py --status red --task "API调用" --note "连接超时"

# 查看近期评分
python traffic_light.py --review --days 7

# 查看统计
python traffic_light.py --stats
```

## 📖 使用示例

### 示例1：集成到AI助手系统

```python
from traffic_light import TrafficLight

class AIAssistant:
    def __init__(self):
        self.scorer = TrafficLight()
    
    def process_task(self, user_message, task_result, error=None):
        # 执行任务...
        
        # 自动评分
        rating = self.scorer.auto_trigger(
            user_message=user_message,
            task_output=str(task_result),
            error=str(error) if error else "",
            task=self.current_task,
            conversation_id=self.conversation_id
        )
        
        if rating:
            print(f"📊 任务评分: {rating['emoji']} {rating['status']}")
            self.log_rating(rating)
        
        return task_result
```

### 示例2：批量评分分析

```python
from traffic_light import TrafficLight

tl = TrafficLight()

# 获取最近30天的评分
recent_ratings = tl.review(days=30)

# 分析解决率
stats = tl.stats()
print(f"解决率: {stats['resolution_rate']}")
print(f"绿灯: {stats['green']}, 黄灯: {stats['yellow']}, 红灯: {stats['red']}")

# 按对话分组
for conv_id in set(r['conversation_id'] for r in recent_ratings if r['conversation_id']):
    conv_ratings = tl.get_by_conversation(conv_id)
    print(f"对话 {conv_id}: {len(conv_ratings)} 次评分")
```

### 示例3：自定义评分规则

```python
from traffic_light import TrafficLight

class CustomTrafficLight(TrafficLight):
    def auto_trigger(self, user_message="", task_output="", error="", task="", conversation_id=""):
        # 自定义评分逻辑
        if "完美" in user_message:
            return self.rate('green', task, '用户表示完美', conversation_id, auto=True)
        elif "需要改进" in user_message:
            return self.rate('yellow', task, '用户建议改进', conversation_id, auto=True)
        
        # 调用父类默认逻辑
        return super().auto_trigger(user_message, task_output, error, task, conversation_id)
```

## 📁 项目结构

```
TrafficLight-Conversation-Tagging-System-skill/
├── traffic_light.py          # 主程序 - 红绿灯评分系统
├── README.md                 # 项目说明文档（本文件）
├── SKILL.md                  # 技能详细说明
├── DEPLOYMENT.md             # 部署指南
├── SSH_DEPLOYMENT_GUIDE.md   # SSH部署故障排除
├── scorer.py                 # 评分器（旧版本）
├── criteria.md               # 评分标准文档
├── score_log.md              # 评分日志示例
├── stats.json                # 统计数据示例
├── test_auto.py              # 自动触发测试
├── test_white.py             # 白灯测试
├── __pycache__/              # Python缓存目录
└── data/
    └── traffic_light.json    # 评分数据存储
```

### 核心文件说明

- **`traffic_light.py`** - 红绿灯评分主程序，包含所有核心功能
- **`SKILL.md`** - 详细的技能使用说明和API文档
- **`data/traffic_light.json`** - 评分数据存储（自动创建）

## 🤝 贡献指南

我们欢迎任何形式的贡献！请参考以下步骤：

### 报告问题
1. 在 [Issues](https://github.com/quick123-666/TrafficLight-Conversation-Tagging-System-skill/issues) 页面查看是否已有类似问题
2. 如果没有，请创建新issue，详细描述问题

### 提交代码
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范
- 遵循 PEP 8 Python代码规范
- 添加适当的注释和文档
- 为新功能添加测试用例
- 确保所有测试通过

### 待开发功能
- [ ] Web界面展示评分数据
- [ ] 更多统计图表和分析
- [ ] 导出为CSV/Excel格式
- [ ] 实时监控仪表板
- [ ] 集成到更多AI助手平台

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

**项目维护者** - quick123-666

**项目链接** - [https://github.com/quick123-666/TrafficLight-Conversation-Tagging-System-skill](https://github.com/quick123-666/TrafficLight-Conversation-Tagging-System-skill)

## 🙏 致谢

感谢以下项目和资源的启发：

- **[Best-README-Template](https://github.com/othneildrew/Best-README-Template)** - 优秀的README模板
- **[ricoLv/Best_README_template](https://github.com/ricoLv/Best_README_template)** - 中文README模板参考
- **所有贡献者和用户** - 感谢你们的反馈和支持

---

<div align="center">
  
**如果这个项目对你有帮助，请给个 ⭐️ 支持一下！**

[![GitHub stars](https://img.shields.io/github/stars/quick123-666/TrafficLight-Conversation-Tagging-System-skill?style=social)](https://github.com/quick123-666/TrafficLight-Conversation-Tagging-System-skill/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/quick123-666/TrafficLight-Conversation-Tagging-System-skill?style=social)](https://github.com/quick123-666/TrafficLight-Conversation-Tagging-System-skill/network/members)

</div>