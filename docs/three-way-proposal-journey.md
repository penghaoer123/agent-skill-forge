# three_way_proposal: 从消失到生产就绪的闭环

## 起点

资产审计发现 `agent/workflows/` 目录已消失，声明式 workflow 的 DAG 定义完好但 runner 代码全部丢失。`three_way_proposal` 处于"YAML 存在但不可执行"状态。

## 终点

```
three_way_proposal:
  node_verification:     passed
  route_verification:    passed
  artifact_verification: passed
  full_dag_execution:    passed
  failure_propagation:   passed
  production_ready:      true
```

基线封存于 `three_way_production_ready_v1.yaml`，不可回写。

## 推进线（同一天内完成）

```
P1      Adapter 验证             26 unit tests, DAG 5 nodes / 3 batches / 0 cycles
P1.5    Runner 数据模型          0 validation errors
P2      Stub 全节点执行          5/5 nodes, artifact 注入验证
P2.5    单节点真实探针           strategic · 34.7s · 2634 chars
P2.6    三节点顺序探针           strategic + engineering + ux, 全部真实模型
P2.7    Synthesis 探针           注入 3 个上游 artifact → 单次调用 → 结构化 JSON
P2.8    Counter-review 探针      安全锁定路由 · Pro 模型 · NEEDS REVISION（3 P0 + 3 P1）
P3      完整 DAG 顺序执行        一条命令 5 节点 · 304.6s · artifact 自动传递
P4      Runner Hardening         failure propagation · 3 场景 · production_ready
```

## 关键架构决策

### 路由分层

| 节点 | Route | 模型 |
|------|-------|------|
| strategic | default | Flash |
| engineering | engineering | Flash |
| ux | ux_review | Flash |
| synthesis | default | Flash |
| counter_review | counter_review | **Pro（安全锁定，禁止降级）** |

### 失败传播（P4）

```
旧: 异常 → "ERROR: xxx" → 注入下游 → 静默污染
新: 异常 → "FAILED: xxx" → blocked 级联 → 阻断所有下游
```

改动极小：仅 `WorkflowInstance.run()` 方法，`failed_steps` + `blocked_steps` 双 set 级联传播。不引入重试、降级、调度重构。

### 执行模式

高上下文会话中 WorkflowInstance 的 `asyncio.gather` 并发导致子进程崩溃。P2.6 起切换到 `subprocess.run` 顺序执行模式，稳定且适合当前服务器。

### Counter-review 超时基线

V4 Pro 在 13.6K prompt 上首次 180s 超时（0 chars），调至 300s 后在 135.5s 完成。保留为运行基线发现，非代码缺陷。

## 资产清单

```
workflows/three_way_proposal/
├── workflow.yaml              # 5-node DAG definition
├── prompts/
│   ├── strategic.md
│   ├── engineering.md
│   ├── ux.md
│   ├── synthesis.md
│   └── counter_review.md

engines/
├── declarative_workflow_adapter.py   # YAML → Composition, 26 tests
├── composition_runner.py             # DAG engine, AgentExecutor protocol
├── test_p2_stub_executor.py          # P2
├── test_p25_strategic_probe.py       # P2.5
├── test_p26_sequential_probe.py      # P2.6
├── test_p27_synthesis_probe.py       # P2.7
├── test_p28_counter_review_probe.py  # P2.8
├── test_p3_full_dag.py               # P3
└── test_p4_failure_propagation.py    # P4
```

所有资产位于用户空间（Skill），Hermes 核心仓库保持干净。

## Counter-review 发现（示例）

Synthesis 生成了一个看似合理但包含三类致命缺陷的方案：

**P0-1** 实现计划调用了不存在的 API（`session_search` 在 bash 脚本中不可用）
**P0-2** 临时文件依赖 `/tmp/`，重启即丢失
**P0-3** 声称三个分析"收敛"，实际是选择性摘樱桃

这证明工作流设计本身有效——它不仅跑通，还阻止了一个包含幻觉 API、易失存储和伪收敛问题的方案。

## 方法论

1. 逐节点验证再组装——不在全链路不通时排查单点故障
2. 成功路径先于故障路径——P3 完整通过后再做 P4 加固
3. 每次改动只改一件事——P4 仅修正失败传播，不顺手加重试/降级/调度
4. 每个阶段有独立验收门——不把"跑通"和"加固"混在同一轮
5. 基线封存后不可回写——后续演进从 v1 出发，用新版本号
