# Python 数据分析课程项目 · 题目四：城市电力负荷分析与预测

3 人小组项目：沈成源（组长）、江玉婷、谭煜霖。完成数据分析全流程：
数据清洗 → 负荷规律分析（日/周/季节）→ 分区对比 → 气象相关性 → 短期负荷预测建模（至少两种模型，MSE/RMSE/R² 评估）。

## 目录结构

```
python/
├── data/
│   ├── raw/      原始数据（题4_城市电力负荷.csv，由 课程要求/数据集 复制而来）
│   └── processed/ 清洗后数据（01 notebook 导出，下游唯一入口）
├── notebooks/   预留目录
├── figures/     图表输出（cleaning/ 为清洗阶段图）
├── tables/      统计表输出
├── project/     已编写的 notebook（01、02、04；03 由沈成源提交，05 由谭煜霖提交）
└── 课程要求/    老师下发的报告模板、要求、数据集
```

## 环境

- Python 3.12，建议用虚拟环境：`python -m venv .venv` 后 `source .venv/Scripts/activate`
- 依赖：`pip install pandas numpy matplotlib jupyter`
- 中文显示：notebook 内已配置 `plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", ...]`

## 运行顺序（notebook）

1. `project/01_data_cleaning.ipynb` —— 清洗，导出 `data/processed/power_load_cleaned.csv`
2. `02_load_patterns.ipynb` —— 日/周/季节负荷规律 + 分区对比（江玉婷）
3. `04_weather_correlation.ipynb` —— 气象-负荷相关性热力图（江玉婷）
4. `03_forecast_model.ipynb` —— 持续性基线、线性回归与随机森林预测对比（沈成源）
5. `05_final_figures.ipynb` —— 成品图统一重绘（谭煜霖）

报告图 1—9 可用 `python project/polish_report_figures.py --apply` 从清洗数据重新生成；不加 `--apply` 时只输出到预览目录。

## 成员分工

| 成员 | 角色 | 负责 notebook |
|---|---|---|
| 沈成源（组长） | 数据工程 + 建模 | 01、03 |
| 江玉婷（GitHub: Lizhuiii） | 规律分析 + 报告主笔 | 02、04；图 A—I |
| 谭煜霖 | 可视化 + 汇报 + 质控 | 05、仓库管理 |

> 报告"小组成员分工与个人承担"章节须与 Git 提交记录一一对应。

江玉婷的图表输出在 `figures/patterns/`（报告图 1—9，文件名 `figA`—`figI`），可复核统计表在 `tables/`；
`02_load_patterns.ipynb` 与 `04_weather_correlation.ipynb` 已保存运行输出，报告数值可直接复现。

## 当前进度

| 模块 | 负责人 | 状态 | 说明 |
|---|---|---|---|
| 仓库初始化、原始数据与报告模板归位 | 江玉婷（协助） | 已完成 | 初始化提交 `a4f05e2` |
| 01 数据清洗 | 沈成源 | 已完成 | 江玉婷曾代沈成源上传执行结果 `cf37f5e`，模块归属仍为沈成源 |
| 02 负荷规律与分区对比 | 江玉婷 | 已完成 | 图 A—F、10 张统计表 |
| 04 气象相关性分析 | 江玉婷 | 已完成 | 图 G—I、5 张统计表 |
| 03 预测建模 | 沈成源 | 已完成（待提交） | 新版 03 已交付，按约定暂不计入江玉婷的提交 |
| 05 成品图统一重绘 | 谭煜霖 | 待完成 | 由谭煜霖负责 |
| 报告图 1—9 视觉优化 | 江玉婷 | 已完成 | 9 张图统一配色、字号、标注与版式；数值与 `tables/` 一致，脚本为 `project/polish_report_figures.py` |
| 报告统稿 | 江玉婷 | 已完成（本地，待补学号） | 20 页、11 图、8 表；第 7 章已补日前预测结论，第 8 章按姓名拆分个人承担；专业与学号待填 |

详细的任务内容、验证结果和 Git 对应关系见 [`PROGRESS.md`](PROGRESS.md)。

## 交付物清单
- [ ] 5 分钟汇报视频（命名：组号_4_沈成源.mp4）
- [ ] 汇报 PPT（命名：组号_4_沈成源.pptx）
- [x] Word 报告电子版（本地已生成，待补专业与学号后提交）
- [ ] 纸质版报告（未来技术学院 418）
