"""Redraw report figures 10-11 in the same visual system as figures 1-9.

The model outputs are read from tables/predictions and tables/model_ablation.csv;
no model is retrained and no metric is recomputed from a different sample.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

from polish_report_figures import (
    GREEN,
    INK,
    MUTED,
    NAVY,
    ORANGE,
    add_footer,
    add_header,
    configure,
    polish_axes,
    thousands,
)


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "processed" / "power_load_cleaned.csv"
PREDICTIONS = ROOT / "tables" / "predictions" / "total_prediction.csv"
ABLATION = ROOT / "tables" / "model_ablation.csv"
OUTPUT = ROOT / "figures" / "model"
PREVIEW = ROOT / "figures" / "model_preview"
TOTAL = "zone_total_power_consumption"


def regression_metrics(actual: np.ndarray, predicted: np.ndarray) -> tuple[float, float]:
    residual = predicted - actual
    rmse = float(np.sqrt(np.mean(residual**2)))
    r2 = float(1 - np.sum(residual**2) / np.sum((actual - actual.mean()) ** 2))
    return rmse, r2


def load_predictions() -> pd.DataFrame:
    frame = pd.read_csv(PREDICTIONS, parse_dates=["datetime"]).set_index("datetime").sort_index()
    cleaned = pd.read_csv(CLEAN, index_col="datetime", parse_dates=True)
    frame["persistence"] = cleaned[TOTAL].shift(144).reindex(frame.index)
    return frame


def prediction_figure(frame: pd.DataFrame, out: Path) -> None:
    actual = frame["y_true"].to_numpy()
    rf_rmse, rf_r2 = regression_metrics(actual, frame["y_pred_rf"].to_numpy())
    persistence_rmse, _ = regression_metrics(actual, frame["persistence"].to_numpy())

    fig = plt.figure(figsize=(8.6, 4.37))
    grid = fig.add_gridspec(
        2,
        1,
        left=0.105,
        right=0.985,
        top=0.72,
        bottom=0.105,
        hspace=0.60,
    )
    full = fig.add_subplot(grid[0])
    zoom = fig.add_subplot(grid[1])

    full.plot(frame.index, frame["y_true"], color=NAVY, linewidth=0.55, alpha=0.92, zorder=4)
    full.plot(frame.index, frame["y_pred_rf"], color=ORANGE, linewidth=0.55, alpha=0.92, zorder=3)
    full.plot(
        frame.index,
        frame["persistence"],
        color="#8C99A4",
        linewidth=0.55,
        linestyle=(0, (3, 2)),
        alpha=0.85,
        zorder=2,
    )
    full.set_xlim(frame.index.min(), frame.index.max())
    full.set_ylim(38000, 102500)
    full.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=(1, 15)))
    full.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    full.set_ylabel("总负荷（kW）")
    full.yaxis.set_major_formatter(FuncFormatter(thousands))
    full.set_title("(a) 整个测试期（2017-11-01—12-30）", loc="left", fontsize=9.4, pad=3)
    polish_axes(full)

    week = frame.loc["2017-11-06":"2017-11-13"]
    zoom.plot(week.index, week["y_true"], color=NAVY, linewidth=1.7, label="实际", zorder=4)
    zoom.plot(week.index, week["y_pred_rf"], color=ORANGE, linewidth=1.30, label="随机森林", zorder=3)
    zoom.plot(
        week.index,
        week["y_pred_lr"],
        color=GREEN,
        linewidth=1.20,
        linestyle=(0, (4, 2)),
        label="线性回归",
        zorder=2,
    )
    zoom.set_xlim(week.index.min(), week.index.max())
    zoom.set_ylim(38000, 102500)
    zoom.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    zoom.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    zoom.set_ylabel("总负荷（kW）")
    zoom.yaxis.set_major_formatter(FuncFormatter(thousands))
    zoom.set_xlabel("日期（2017 年）")
    zoom.set_title("(b) 放大一周（11-06—11-13）", loc="left", fontsize=9.2, pad=3)
    polish_axes(zoom)

    handles = [
        Line2D([0], [0], color=NAVY, linewidth=1.6, label="实际"),
        Line2D([0], [0], color=ORANGE, linewidth=1.4, label="随机森林"),
        Line2D([0], [0], color="#8C99A4", linewidth=1.3, linestyle=(0, (3, 2)), label="持续性基线"),
        Line2D([0], [0], color=GREEN, linewidth=1.3, linestyle=(0, (4, 2)), label="线性回归"),
    ]
    fig.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(0.105, 0.815),
        ncol=4,
        frameon=False,
        handlelength=1.8,
        columnspacing=1.35,
        fontsize=7.7,
    )

    add_header(
        fig,
        "测试期预测：随机森林整体贴近实际负荷",
        f"测试集 {len(frame):,} 条；随机森林 RMSE {rf_rmse:,.1f} kW、R² {rf_r2:.4f}，"
        f"相对持续性基线降低 {(1 - rf_rmse / persistence_rmse) * 100:.1f}%",
    )
    add_footer(fig, "数据：2017 年 11—12 月测试集 8,640 条 · 10 分钟采样")
    fig.savefig(out / "fig10_pred_vs_actual.png", dpi=240)
    plt.close(fig)


def ablation_figure(out: Path) -> None:
    table = pd.read_csv(ABLATION)
    configs = list(dict.fromkeys(table["特征配置"]))
    linear = table[table["模型"] == "线性回归"].set_index("特征配置").reindex(configs)
    forest = table[table["模型"] == "随机森林"].set_index("特征配置").reindex(configs)

    labels = ["S1\n仅时间+气象", "S2\n+lag_144", "S3\n全部特征"]
    x = np.arange(len(configs))
    linear_r2 = linear["R²"].to_numpy(dtype=float)
    forest_r2 = forest["R²"].to_numpy(dtype=float)
    forest_rmse = forest["RMSE"].to_numpy(dtype=float)

    fig, (left, right) = plt.subplots(1, 2, figsize=(8.6, 3.15), gridspec_kw={"width_ratios": [1.45, 1.0]})
    fig.subplots_adjust(left=0.075, right=0.985, top=0.63, bottom=0.21, wspace=0.36)

    width = 0.34
    left.axhline(0, color="#8A96A0", linewidth=0.8, zorder=1)
    left.bar(x - width / 2, linear_r2, width, color=GREEN, label="线性回归", zorder=3)
    left.bar(x + width / 2, forest_r2, width, color=ORANGE, label="随机森林", zorder=3)
    for position, value in zip(x - width / 2, linear_r2):
        below = value < 0
        left.text(
            position,
            value - 0.055 if below else value + 0.025,
            f"{value:.3f}",
            ha="center",
            va="top" if below else "bottom",
            fontsize=7.3,
            color=INK,
        )
    for position, value in zip(x + width / 2, forest_r2):
        left.text(
            position,
            value + 0.025,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=7.3,
            color=INK,
        )
    left.set_xticks(x)
    left.set_xticklabels(labels, fontsize=7.5)
    left.set_ylim(-1.08, 1.14)
    left.set_yticks([-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0])
    left.set_ylabel("R²", fontsize=8.2)
    left.set_title("(a) 不同特征配置的 R²", loc="left", fontsize=9.4, pad=4)
    left.legend(loc="lower right", frameon=False, fontsize=7.0, handlelength=1.2)
    polish_axes(left)

    bars = right.bar(x, forest_rmse, width=0.52, color=ORANGE, zorder=3)
    for bar, value in zip(bars, forest_rmse):
        right.text(
            bar.get_x() + bar.get_width() / 2,
            value + 55,
            f"{value:,.0f}",
            ha="center",
            va="bottom",
            fontsize=7.3,
            color=INK,
        )
    right.set_xticks(x)
    right.set_xticklabels(labels, fontsize=7.5)
    right.set_ylim(0, 4520)
    right.set_ylabel("RMSE（kW）", fontsize=8.2)
    right.set_title("(b) 随机森林 RMSE", loc="left", fontsize=9.4, pad=4)
    polish_axes(right)

    add_header(
        fig,
        "特征消融：历史负荷是主要增益来源",
        "S1 仅时间+气象，S2 加入 lag_144，S3 全部特征\n"
        f"随机森林 RMSE 由 {forest_rmse[0]:,.0f} kW 降至 {forest_rmse[-1]:,.0f} kW"
        f"（合计 −{(1 - forest_rmse[-1] / forest_rmse[0]) * 100:.1f}%）；"
        f"加入 lag_144 一步降低 {(1 - forest_rmse[1] / forest_rmse[0]) * 100:.1f}%，"
        f"其余特征再降低 {(1 - forest_rmse[-1] / forest_rmse[1]) * 100:.1f}%",
    )
    add_footer(fig, "数据：tables/model_ablation.csv · 测试集 8,640 条")
    fig.savefig(out / "fig11_feature_ablation.png", dpi=240)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write new figures into figures/model")
    parser.add_argument("--out", type=Path, help="write figures to this directory")
    arguments = parser.parse_args()

    configure()
    target = arguments.out or (OUTPUT if arguments.apply else PREVIEW)
    target.mkdir(parents=True, exist_ok=True)
    prediction_figure(load_predictions(), target)
    ablation_figure(target)
    print(f"figures written to {target}")


if __name__ == "__main__":
    main()
