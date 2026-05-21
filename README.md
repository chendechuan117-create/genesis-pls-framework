# Genesis PLS Framework

以 **Yogg 放生模式** 为主线提取的 Genesis 点线面（Point-Line-Surface, PLS）框架。

这个仓库不是完整 Genesis 产品宣传页，也不是一份带有作者私有知识库的运行快照。它保留的是一条可供他人复现和改造的最小事实路径：

```text
yogg_auto.py
  -> genesis.auto_mode.run_auto()
  -> V4Loop(..., disable_multi_g=True, c_phase_blocking=True)
  -> search_knowledge_nodes / record_point / record_line
  -> NodeVault(SQLite) + SurfaceExpander
```

私有 `.env`、SQLite 知识库、trace 数据、运行日志、个人探索产物不包含在本仓库中。在没有本地旧库迁移的情况下，首次运行会从空库开始建立自己的点线面。

---

## 代码依据

下面这些路径是本文档描述的依据，而不是宣传性抽象：

- **`yogg_auto.py`**：声明 Yogg 是“无 Discord 依赖的独立 auto runner”，设置 session 轮数、dry limit、自进化开关、崩溃回滚和内存看门狗。
- **`genesis/auto_mode.py::run_auto`**：定义自主循环、默认 directive、round timeout、PLS terrain/branch signals，以及实际调用 `agent.process(...)` 的位置。
- **`genesis/v4/loop.py::V4Loop`**：读取 `loop_config["disable_multi_g"]`，在 Yogg 路径中跳过 Lens/Multi-G；`c_phase_blocking=True` 时同步等待 C-Phase。
- **`genesis/tools/node_tools.py`**：`record_point` / `record_line` 的工具 schema 和写入规则。
- **`genesis/tools/search_tool.py`**：`search_knowledge_nodes` 命中后触发 Surface 装配。
- **`genesis/v4/surface.py`**：`SurfaceExpander.expand_surface()` 的三层组装逻辑：基础、推进、共场。
- **`genesis/v4/manager.py::NodeVault`**：默认 SQLite 存储位置和 PLS 拓扑相关持久化。

---

## 这是什么

Yogg 模式是 Genesis 的独立自主运行入口。它不依赖 Discord 输入，不需要用户在每轮手动发指令，而是把一个长期方向交给 `run_auto()`，让系统按轮次持续探索、执行、记录和重启。

这个仓库关注的不是“多 Agent 展示效果”，而是一个更小的问题：

```text
一个每轮都会失忆的 LLM，如何在下一轮继承过去的探索痕迹？
```

PLS 给出的答案不是把所有历史塞回上下文，而是把历史压成三类结构：

- **点（Point）**：某一轮 LLM 形成的可复用理解。
- **线（Line）**：新理解基于哪些旧理解产生。
- **面（Surface）**：每轮搜索后，从点线拓扑中临时装配出的当轮认知场。

---

## Yogg 放生模式的实际边界

本 README 描述的是 Yogg 路径，不描述完整 Genesis 仓库中所有历史模块。

### 使用中的路径

- **独立入口**：`yogg_auto.py`
- **自主循环**：`genesis/auto_mode.py::run_auto`
- **Agent 构造**：`factory.py::create_agent`
- **主循环执行**：`genesis/v4/loop.py::V4Loop`
- **点线写入**：`genesis/tools/node_tools.py::RecordPointTool` / `RecordLineTool`
- **搜索与面装配**：`genesis/tools/search_tool.py` + `genesis/v4/surface.py`
- **持久存储**：`genesis/v4/manager.py::NodeVault`

### Yogg 路径中明确关闭或弱化的东西

- **Discord 不是输入入口**：`yogg_auto.py` 用 `LogChannel` 模拟 `channel.send()`，输出到日志；Discord webhook 只是可选的单向输出。
- **Multi-G 默认不参与**：`run_auto()` 调用 `agent.process(..., loop_config={"disable_multi_g": True, ...})`，V4Loop 会跳过 Lens 阶段。
- **C-Phase 是阻塞的**：`c_phase_blocking=True`，每轮等待反思完成后再进入下一轮。
- **后台 Daemon 不是主线**：这个模板不依赖外部后台知识代谢服务才能运行。
- **代码写入应进 Doctor 沙箱**：Yogg prompt 要求代码修改通过 `doctor.sh` 在沙箱中完成；这是一条运行约束，不应宣传成“任意 shell 都绝对安全”。

---

## PLS：按实现理解，而不是按口号理解

### 1. 点：`record_point`

`record_point` 写入轻量知识点。实现上：

- 默认类型是 `CONTEXT`。
- 只有经过验证、可复用的强结晶经验才应显式写成 `LESSON`。
- 不提供 `node_id` 时，会生成 `P_` 前缀的稳定 ID。
- 写入后返回 ID，并提示继续用 `record_line` 连接它基于哪些已有点。

点不是“客观事实条目”。更准确地说，点是某一轮模型接触对象后形成的理解切片。它可能片面，也可能后来被修正。因此 PLS 不靠单个点的自我声明来判断价值。

### 2. 线：`record_line`

`record_line` 写入一条推理依赖：

```text
new_point_id --[based_on]--> basis_point_id
```

它回答的问题是：

```text
为什么这个新点是基于那个旧点产生的？
```

实现边界：

- 线不是代码调用关系。
- 线不是评分。
- 线要求 `new_point_id`、`basis_point_id`、`reasoning` 都存在。
- 自引用会被拒绝。
- 不存在、隐藏、virtual 等不可连线端点会被拒绝。
- 同一轮内形成的线会被标记为“同轮”。

PLS 设计里，同轮线只能记录因果，不能当成独立验证。只有跨轮、跨上下文的再次踩踏，才说明某个旧点真的在被后来的探索反复依赖。

### 3. 面：`SurfaceExpander`

面不是持久表，也不是一份“总结”。它是搜索之后的临时上下文切片：

```text
search_knowledge_nodes
  -> 得到种子点
  -> SurfaceExpander.expand_surface(seed_ids)
  -> 渲染基础 / 探索 / 游离 等角色标签
  -> 注入当轮 GP 上下文
  -> 本轮结束后丢弃
```

`genesis/v4/surface.py` 里，面有三层：

- **基础层**：沿入线较高的路径 BFS，优先踩稳被反复使用过的推理通道。
- **推进层**：把部分低价值填充点替换成前沿点，避免只在旧路里打转。
- **共场层**：放入少量未被显性路径消费的“游离”点，让模型有机会产生“这两个是否有关”的弱联想。

角色标签来自拓扑结构，不是模型自己夸自己：

- **基础**：入线数达到当前库分布的 P75 阈值。
- **探索**：未达到基础阈值的前沿点。
- **游离**：不在当前显性路径上，只是被安排共同出现。

GP 常规只看到定性标签，不看到精确入线数。这个边界是故意的：如果模型能看到数字，它容易追逐数字而不是判断推理是否合理。

---

## Yogg 每轮发生什么

简化后的真实流程如下：

```text
1. yogg_auto.py 加载 .env，并设置 Yogg 默认环境变量
2. 启动前崩溃守卫检查是否需要回滚自进化失败
3. create_agent() 注册工具并创建 GenesisV4 agent
4. _run_session() 创建 LogChannel，把输出写到 runtime/yogg_logs/
5. run_auto() 生成本轮 prompt 和系统信号
6. agent.process(..., disable_multi_g=True, c_phase_blocking=True)
7. GP 搜索知识、读取文件、必要时派发执行
8. 若形成新理解，用 record_point 写点，再用 record_line 写依据
9. C-Phase 阻塞运行，基于真实执行结果做反思
10. 记录 round report；session 结束后可交给 systemd 重启
```

Yogg 不是靠一次长上下文硬撑。它依靠：

- SQLite 中持久存在的点和线。
- 搜索时临时装配出的面。
- 每轮反思后的新写入。
- systemd 或外层 runner 对长时间运行的重启兜底。

---

## 存储与空白性

本模板不会上传任何私有知识库。

运行时默认路径：

```text
~/.genesis/workshop_v4.sqlite
```

注意：`NodeVault` 如果发现 `~/.genesis/workshop_v4.sqlite` 不存在、但 `~/.nanogenesis/workshop_v4.sqlite` 存在，会把旧库迁移到新路径。若你需要真正空白运行，请先移开这两个本地文件。

仓库中的 `.gitignore` 会排除：

- `.env`
- `*.sqlite`
- `*.db`
- `runtime/*`
- 日志、备份、patch、临时文件

因此，新用户 clone 后得到的是空白结构，不会继承原作者的点线面内容、API key、trace 数据或私有实验记录。

---

## 快速开始

### 1. 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置 `.env`

最小配置：

```env
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
GENESIS_MODEL=deepseek/deepseek-reasoner
```

建议保留 round 级超时：

```env
GENESIS_AUTO_ROUND_TIMEOUT_SECS=600
```

如只想先观察 PLS，不希望自动应用自进化补丁，可以显式关闭：

```env
GENESIS_SELF_EVOLUTION=0
```

### 3. 准备 Doctor 沙箱

Yogg 的 prompt 约束要求代码修改通过 `doctor.sh` 进入沙箱。运行前建议启动：

```bash
cd doctor
docker compose up -d
```

如果你的环境使用旧版 Docker Compose：

```bash
cd doctor
docker-compose up -d
```

### 4. 前台运行 Yogg

```bash
python -u yogg_auto.py "围绕一个你关心的系统概念进行 PLS 探索"
```

不传参数时，会使用 `auto_mode.py` 中的默认方向：围绕 Genesis/Yogg 的概念整体进行 PLS 概念面探索。

---

## 目录说明

```text
genesis/
  auto_mode.py              Yogg 自主循环与 prompt 组装
  core/                     基础抽象、provider、registry、tracer
  providers/                LLM provider 适配
  tools/
    node_tools.py           record_point / record_line 等知识写入工具
    search_tool.py          search_knowledge_nodes 与 Surface 注入点
  v4/
    loop.py                 G/Op/C 主循环与 disable_multi_g 逻辑
    manager.py              NodeVault(SQLite) 与 PLS 拓扑存储
    surface.py              SurfaceExpander 三层面装配
doctor/                     Docker 沙箱
yogg_auto.py                独立放生模式 runner
factory.py                  provider 与工具注册入口
tests/                      行为与回归测试
```

---

## 设计边界

PLS 不是：

- 不是向量库换皮。
- 不是把代码依赖图塞给 LLM。
- 不是用 confidence 数字给知识打分。
- 不是让模型反复复述已有节点。
- 不是把旧知识自动判定为真理。

PLS 要解决的是一个更具体的问题：

```text
如何让多个离散 LLM 调用之间，保留“我基于什么产生了什么”的推理足迹，
并在下一轮只取出足够相关、足够有张力、但不过度拥挤的一小片上下文。
```

如果你要改造这个框架，优先保护三个不变量：

- **同轮隔离**：同一次调用内的连线不能当成独立验证。
- **因果写线**：新点写入后必须说明它基于哪些旧点产生。
- **数字不可见**：GP 看到角色标签，而不是精确入线数、胜率或融合分。

---

## License

MIT. See [LICENSE](LICENSE).
