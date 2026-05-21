# Genesis PLS Framework — 基于点线面记忆代谢的 AI Agent 内核

Genesis PLS (Point-Line-Surface) Framework 是一个具备**活性知识代谢能力**的 AI Agent 内核架构。

其核心设计哲学：**云 API 是意识，本地机器是身体，元信息系统（点线面）是神经**。Agent 系统在执行任务的同时，能够持续地在本地数据库中自主学习、验证、代谢知识，维持状态的连续性。

---

## 🌌 核心机制：点线面（PLS）元记忆系统

在传统的 Agent 记忆中，记忆往往被视为静态的、堆积式的。Genesis 采用 **点（Point）、线（Line）、面（Surface）** 的拓扑图谱来构建 Agent 的时间和认知流。

1. **点 (Point / 知识节点)**：代表 Agent 沉淀的原子事实、经验 (LESSON)、背景 (CONTEXT)、资产 (ASSET) 等。
2. **线 (Line / 拓扑关系)**：节点之间的语义关联，如 `PREREQUISITE` (前置条件), `RESOLVES` (解决问题), `RELATED_TO` (关联), `CONTRADICTS` (矛盾)。线是有生命周期的，根据实际任务执行结果动态强化或衰减。
3. **面 (Surface / 激活表面)**：根据当前的任务和对话上下文，动态从数据库中“提起”相关的点与线，构成一个局部稠密的上下文表面。这个激活面充当了 Agent 的动态世界模型，供其在后续的规划中进行“碰撞”和推理。

---

## 🧠 核心架构：三体认知管线 (G-Op-C)

为了防止执行时的上下文污染，框架通过 **Context Firewall** 实现了极其严格的上下文隔离：

```
                    ┌─────────────────────────┐
                    │      用户请求 / 任务      │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │     Multi-G 多人格透镜    │  <--- 3~7个 MBTI 人格并行检索分析并合并
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │     G-Process (思考者)   │  <--- 规划 + 知识检索 + 蓝图分派
                    └────────────┬────────────┘
                                 ▼ [Context Firewall / 隔绝历史噪音]
                    ┌─────────────────────────┐
                    │    Op-Process (执行者)  │  <--- 纯净上下文，原子任务，物理工具调用 (Shell/File/Web)
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │    C-Process (反思者)   │  <--- 提炼经验、物理结果去重、写入点线面
                    └─────────────────────────┘
```

- **G-Process (Thinking)**：只面对知识库(NodeVault)和用户请求，负责策略规划与子任务分配。
- **Op-Process (Executing)**：处于严格的“上下文防火墙”之后，不包含用户的原始历史，只根据 G 给出的局部蓝图进行工具调用（读写文件、沙箱操作等）。
- **C-Process (Reflecting)**：在任务结束后单轮运行，根据 Op 的真实执行结果进行知识提炼（LESSON），并对引用的知识节点进行客观反馈（Arena 胜负评估），升降其置信度。

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
在项目根目录创建 `.env` 文件，配置 API 密钥与代理：
```env
# 核心 LLM API 配置
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# AI 代理网络代理配置 (可选)
# SOCKS_PROXY=socks5://127.0.0.1:20170
```

### 3. 工具与沙箱环境
Agent 的物理执行通过 `doctor/` 下的 Docker 沙箱实现。这可以确保 Agent 在执行 Shell 命令或进行实验时不会破坏宿主机：
```bash
# 启动沙箱
cd doctor
docker-compose up -d
```

### 4. 运行 Agent
```bash
# 运行默认独立放生循环 (Yogg 模式)
python yogg_auto.py "探索自进化并编写测试案例"
```

---

## 📂 目录结构与关键文件

- `genesis/` — 核心包目录
  - `core/` — 运行时核心，包括基础工具类、沙箱通信、调用追踪等
  - `providers/` — 云端 LLM 的接入适配层
  - `skills/` — Agent 的物理技能与特定工具实现 (如浏览器、系统状态监控等)
  - `tools/` — 统一的工具注册与调用层
  - `v4/` — PLS 机制、黑板、多人格透镜、双竞技场（Arena）及后台代谢 Daemon 的核心实现
- `doctor/` — 物理沙箱 Docker 配置文件，保障执行时的环境安全性与隔离性
- `tests/` — 核心行为与各组件的模块化测试集
- `yogg_auto.py` — 无需外部组件依赖的独立自主迭代 Runner (放生模式)
- `factory.py` — 工具与 Agent 实例的注册装配工厂

---

## ⚖️ 开源协议

本项目采用 MIT 协议开源。详情参见 [LICENSE](LICENSE) 文件。
