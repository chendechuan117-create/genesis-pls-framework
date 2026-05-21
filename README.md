# Genesis PLS Template (Yogg Mode) — 极简点线面记忆代谢 Agent 内核

Genesis PLS (Point-Line-Surface) Template 是以 **Yogg 放生模式 (Auto Mode)** 为主干的高效自主 Agent 内核。

其核心设计哲学：**云 API 是意识，本地机器是身体，元信息系统（点线面）是神经**。去除所有不必要的外部组件与服务，实现 100% 纯净、独立的本地思考执行循环。

---

## 🌌 Yogg 放生模式与点线面（PLS）机制

Yogg 模式是一个**无 Discord 依赖、无外部后台 Daemon 干扰、无多人格透镜开销**的极简自主闭环。Agent 仅通过单一主进程持续循环执行任务，并在执行过程中完成知识代谢。

### 1. 拓扑图谱元记忆 (PLS)
- **点 (Point)**：沉淀出的原子经验节点 (LESSON/CONTEXT/ASSET/VOID)。
- **线 (Line)**：节点之间的显式依赖关联 (PREREQUISITE/RESOLVES/CONTRADICTS)。线是有生命周期的，根据实际任务执行结果动态强化或衰减。
- **面 (Surface)**：每一轮任务中，根据当前上下文，通过 BFS/拓扑遍历从数据库中“提起”相关的点与线，构成一个局部稠密的上下文激活表面，作为下轮 G 的注意力候选。

### 2. 三体认知管线 (G-Op-C 与 上下文防火墙)
```text
                    ┌─────────────────────────┐
                    │      Session Planner    │  <--- 信号驱动：根据历史错误与空洞确定议程
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │     G-Process (思考者)   │  <--- 策略规划 + 知识检索 + 蓝图分派
                    └────────────┬────────────┘
                                 ▼ [Context Firewall / 隔绝历史噪音]
                    ┌─────────────────────────┐
                    │    Op-Process (执行者)  │  <--- 纯净上下文，在 Docker 沙箱中调用物理工具
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │    C-Process (反思者)   │  <--- 反思物理结果、提炼 LESSON、写入点线面
                    └─────────────────────────┘
```
- **Context Firewall (上下文防火墙)**：Op 在执行时，拿不到用户的原始历史与漫长的思考噪音，只专注于 G 派发给它的当前原子蓝图。
- **G-Process**：负责“想”，在激活的知识面与任务之间进行规划。
- **Op-Process**：负责“做”，在严格隔离的 Docker 沙箱容器中运行，完全保障宿主机安全。
- **C-Process**：负责“学”，在任务结束后单轮运行，针对 Op 的物理修改进行反思并提炼写回。

---

## 🛠️ 快速开始

### 1. 环境准备
确保您的系统安装了 Python 3.10+ (推荐 Python 3.12+)。
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置文件
在项目根目录创建 `.env` 文件，配置 API 密钥：
```env
# 核心 LLM API 配置
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# Yogg 超时设置 (推荐 600s 保护，防止网络僵死)
GENESIS_AUTO_ROUND_TIMEOUT_SECS=600
```

### 3. 工具与沙箱环境
Agent 的物理执行通过 `doctor/` 下的 Docker 沙箱实现：
```bash
# 启动沙箱
cd doctor
docker-compose up -d
```

### 4. 运行 Agent (Yogg 模式)
```bash
# 启动放生循环
python yogg_auto.py "探索自进化并编写测试案例"
```

---

## 📂 目录结构与关键文件

- `genesis/` — 核心包目录
  - `core/` — 运行时核心，包括基础工具类、沙箱通信、调用追踪等
  - `providers/` — 云端 LLM 的接入适配层
  - `skills/` — Agent 的物理技能与特定工具实现
  - `tools/` — 统一的工具注册与调用层 (包含 `node_tools.py`, `search_tool.py` 等)
  - `v4/` — 核心 PLS 机制、黑板、双竞技场（Arena）及自学习签名的实现
- `doctor/` — 物理沙箱 Docker 配置文件，保障执行时的环境隔离
- `tests/` — 核心行为与各组件的模块化测试集
- `yogg_auto.py` — 无需外部组件依赖 of 独立自主迭代 Runner (放生模式)
- `factory.py` — 工具与 Agent 实例的注册装配工厂

---

## ⚖️ 开源协议

本项目采用 MIT 协议开源。详情参见 [LICENSE](LICENSE) 文件。
