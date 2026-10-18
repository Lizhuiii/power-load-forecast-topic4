# Python 数据分析课程项目 · 题目四：城市电力负荷分析与预测

3 人小组项目（A 组长 / B / C）。完成数据分析全流程：
数据清洗 → 负荷规律分析（日/周/季节）→ 分区对比 → 气象相关性 → 短期负荷预测建模（至少两种模型，MSE/RMSE/R² 评估）。

## 目录结构

```
python/
├── data/
│   ├── raw/      原始数据（题4_城市电力负荷.csv，由 课程要求/数据集 复制而来）
│   └── processed/ 清洗后数据（01 notebook 导出，下游唯一入口）
├── notebooks/   各分析 notebook（当前 01 暂放在 project/ 下）
├── figures/     图表输出（cleaning/ 为清洗阶段图）
├── tables/      统计表输出
├── project/     执行计划、已编写的 notebook
└── 课程要求/    老师下发的报告模板、要求、数据集
```

## 环境

- Python 3.12，建议用虚拟环境：`python -m venv .venv` 后 `source .venv/Scripts/activate`
- 依赖：`pip install pandas numpy matplotlib jupyter`
- 中文显示：notebook 内已配置 `plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", ...]`

## 运行顺序（notebook）

1. `project/01_data_cleaning.ipynb` —— 清洗，导出 `data/processed/power_load_cleaned.csv`
2. `02_load_patterns.ipynb` —— 日/周/季节负荷规律 + 分区对比（B）
3. `04_weather_correlation.ipynb` —— 气象-负荷相关性热力图（B）
4. `03_forecast_model.ipynb` —— 线性回归 vs 随机森林 预测对比（A）
5. `05_final_figures.ipynb` —— 成品图统一重绘（C）

## 成员分工

| 成员 | 角色 | 负责 notebook |
|---|---|---|
| A（组长） | 数据工程 + 建模 | 01、03 |
| B | 规律分析 + 报告主笔 | 02、04 |
| C | 可视化 + 汇报 + 质控 | 05、仓库管理 |

> 报告"小组成员分工与个人承担"章节须与 Git 提交记录一一对应。
