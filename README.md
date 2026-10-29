# Python 数据分析课程项目 · 题目四：城市电力负荷分析与预测

3 人小组项目：沈成源（组长）、江玉婷、谭煜霖。完成数据分析全流程：
数据清洗 → 负荷规律分析（日/周/季节）→ 分区对比 → 气象相关性 → 短期负荷预测建模（至少两种模型，MSE/RMSE/R² 评估）。

## 目录结构

```
python/
├── data/
│   ├── raw/      原始数据（题4_城市电力负荷.csv，由 课程要求/数据集 复制而来）
│   └── processed/ 清洗后数据（01 notebook 导出，下游唯一入口）
├── notebooks/   前期 EDA 成品图绘制代码
├── figures/     图表输出（cleaning/ 清洗阶段图、model/ 建模图 300 dpi、patterns/ 规律分析图）
├── tables/      统计表输出（含 predictions/ 预测结果）
├── project/     已编写的 notebook（01、02、04；03 由沈成源提交，05 由谭煜霖提交）
├── report/      报告成品（Word、PDF）
└── 课程要求/    老师下发的报告模板、要求、数据集
```

## 环境

- Python 3.12，建议用虚拟环境：`python -m venv .venv` 后 `source .venv/Scripts/activate`
- 依赖：`pip install pandas numpy matplotlib jupyter scikit-learn`
- 中文显示：notebook 内已配置 `plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", ...]`

## 运行顺序（notebook）

| 顺序 | notebook | 内容 | 负责人 | 状态 |
|---|---|---|---|---|
| 1 | `project/01_data_cleaning.ipynb` | 清洗，导出 `data/processed/power_load_cleaned.csv` | 沈成源 | ✅ |
| 2 | `project/02_load_patterns.ipynb` | 日/周/季节负荷规律 + 分区对比 | 江玉婷 | ✅ |
| 3 | `project/04_weather_correlation.ipynb` | 气象-负荷相关性热力图 | 江玉婷 | ✅ |
| 4 | `project/03_forecast_model.ipynb` | 持续性基线、线性回归与随机森林预测对比 | 沈成源 | ✅ |
| 5 | `project/05_final_figures.ipynb` | 成品图统一重绘 | 谭煜霖 | ✅ |

> `03` 依赖 `data/processed/power_load_cleaned.csv`，须先跑 `01`。
> 报告图 1—9 可用 `python project/polish_report_figures.py --apply` 从清洗数据重新生成；报告图 10—11 可用 `python project/polish_model_figures.py --apply` 从预测表和消融表重新生成。两者不加 `--apply` 时都只输出到预览目录。

## 建模结果摘要（03_forecast_model）

预测口径：**日前（day-ahead）**，特征只用 ≥1 天前的观测；训练 2017-01-08～10-31，测试 2017-11-01～12-30。

| 模型 | RMSE (kW) | MAE (kW) | R² | MAPE |
|---|---|---|---|---|
| 持续性基线（抄前一日同时刻） | 3,228.6 | 2,120.3 | 0.9484 | 3.40% |
| 线性回归 | 2,429.0 | 1,795.1 | 0.9708 | 2.89% |
| **随机森林** | **2,301.7** | **1,639.5** | **0.9738** | **2.64%** |

关键结论（详见 notebook 步骤 11）：

1. 随机森林只在**总负荷**上最优（较线性回归 RMSE 低 5.2%），但在 Zone1/Zone2 上**线性回归更好**，Zone3 上三个模型**全部不如持续性基线**——汇总指标会掩盖分区差异。
2. Zone3 的误差来自**分布漂移**（8–9 月负荷退出）：RMSE 11 月约 1,790 kW、12 月降到约 710 kW，随水平稳定而衰减。对策是滚动重训练，而非换模型。
3. 特征重要性 `lag_144` 占 94.6%。消融显示：仅时间+气象时随机森林 R²=0.924（冷启动可用），加入 `lag_144` 后升到 0.971；但**线性回归在仅时间+气象时 R²=−0.883**，是 `dayofyear` 线性外推的经典灾难。
4. 测试期残差均值 +639 kW，早 7 时偏差最大（+1,667 kW），冬季早高峰爬坡被系统性高估。

### 图表与预测文件（供谭煜霖出图 / PPT 使用）

- **图表**：`figures/model/fig01~fig06_*.png`，统一 **300 dpi**，命名规则 `fig0N_主题.png`
  - 报告用图另存为 `figures/model/fig10_pred_vs_actual.png`、`fig11_feature_ablation.png`，由 `project/polish_model_figures.py` 生成，原始 `fig01`—`fig06` 保留不动

  | 文件 | 内容 |
  |---|---|
  | `fig01_pred_vs_actual.png` | 测试期预测 vs 实际（全期 + 一周放大） |
  | `fig02_scatter.png` | 三模型预测散点 |
  | `fig03_feature_importance.png` | 随机森林特征重要性 Top15 |
  | `fig04_error_breakdown.png` | 分月 RMSE + 分区偏差率 |
  | `fig05_residual_hour.png` | 残差按小时分布 |
  | `fig06_ablation.png` | 特征消融（S1/S2/S3） |

- **预测结果**：`tables/predictions/`

  | 文件 | 列 | 行数 |
  |---|---|---|
  | `total_prediction.csv` / `zone1~zone3_prediction.csv` | `datetime, y_true, y_pred_lr, y_pred_rf` | 8,640（测试期） |
  | `s1_lr_prediction.csv` | `datetime, y_true, y_pred, residual` | 8,640（S1 仅时间+气象的线性回归） |

> `s1_lr_prediction.csv` 用于核对 fig06 里那根 R²=−0.883 的负柱子：**不是预测值爆炸，而是随外推距离增大的系统性低估**（11 月低估 12,114 kW、12 月低估 22,889 kW，全期平均低估 17,501 kW）。

## 成员分工

| 成员 | 角色 | 负责 notebook |
|---|---|---|
| 沈成源（组长） | 数据工程 + 建模 | 01、03 |
| 江玉婷（GitHub: Lizhuiii） | 规律分析 + 报告主笔 | 02、04；报告图 1—9 |
| 谭煜霖 | 可视化 + 汇报 + 质控 | 05、仓库管理 |

> 报告"小组成员分工与个人承担"章节须与 Git 提交记录一一对应。

江玉婷的图表输出在 `figures/patterns/`（报告图 1—9，文件名 `figA`—`figI`），可复核统计表在 `tables/`；
`02_load_patterns.ipynb` 与 `04_weather_correlation.ipynb` 已保存运行输出，报告数值可直接复现。

## 当前进度

| 模块 | 负责人 | 状态 | 说明 |
|---|---|---|---|
| 仓库初始化、原始数据与报告模板归位 | 江玉婷（协助） | 已完成 | 初始化提交 `a4f05e2` |
| 01 数据清洗 | 沈成源 | 已完成 | 江玉婷曾代沈成源上传执行结果 `cf37f5e`，模块归属仍为沈成源 |
| 02 负荷规律与分区对比 | 江玉婷 | 已完成 | 报告图 1—6、10 张统计表 |
| 04 气象相关性分析 | 江玉婷 | 已完成 | 报告图 7—9、5 张统计表 |
| 03 预测建模 | 沈成源 | 已完成 | 3 个模型对比 + 特征消融；图 01—06（300 dpi）、`tables/predictions/`；合并时带入的冲突标记已清理，内容与 `b492669` 一致 |
| 05 成品图统一重绘 | 谭煜霖 | 已完成 | `project/05_final_figures.ipynb` 已规范为仓库相对路径；输出 4 张图到 `figures/cleaning/` |
| 报告图 1—9 视觉优化 | 江玉婷 | 已完成 | 9 张图统一配色、字号、标注与版式；数值与 `tables/` 一致，脚本为 `project/polish_report_figures.py` |
| 报告图 10—11 视觉优化 | 江玉婷 | 已完成 | 图 10、图 11 与图 1—9 统一配色、字号和标注；数据直接取自 `tables/predictions/` 与 `tables/model_ablation.csv`，脚本为 `project/polish_model_figures.py` |
| 报告统稿 | 江玉婷 | 已完成 | 20 页、11 图、8 表；第 7 章已补日前预测结论，第 8 章按姓名拆分个人承担；学号和署名已填，专业栏按模板留空手填；已补 9.4 交付清单与预热期样本说明 |

详细的任务内容、验证结果和 Git 对应关系见 [`PROGRESS.md`](PROGRESS.md)。

## 交付物清单
- [x] 5 分钟汇报视频（命名：组号_4_沈成源.mp4，谭煜霖提交）
- [x] 汇报 PPT（命名：组号_4_沈成源.pptx，谭煜霖提交）
- [x] Word 报告电子版（20 页、11 图、8 表；学号与署名已填，专业栏留空手填）
- [ ] 纸质版报告（未来技术学院 418）
