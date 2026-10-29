"""Regenerate the report figures with one visual system.

The analytical values are unchanged. All figures are recomputed from the
cleaned 10-minute series so the report and the repository share one source.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "power_load_cleaned.csv"
FIG_DIR = ROOT / "figures" / "patterns"
PREVIEW_DIR = ROOT / "figures" / "patterns_polished"

TOTAL = "zone_total_power_consumption"
ZONES = {
    "Zone1": "zone1_power_consumption",
    "Zone2": "zone2_power_consumption",
    "Zone3": "zone3_power_consumption",
}

INK = "#1F2933"
MUTED = "#5F6B76"
GRID = "#DDE3E8"
NAVY = "#1F4668"
ORANGE = "#D9773B"
GREEN = "#2F8F72"
BRICK = "#B84C46"
ZONE_COLORS = [ORANGE, GREEN, BRICK]
SOFT_BLUE = "#EAF1F7"
SOFT_ORANGE = "#FAEDE3"
WEEKEND = "#C9854F"


def configure() -> None:
    plt.rcParams.update(
        {
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
            "axes.unicode_minus": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "savefig.dpi": 240,
            "figure.dpi": 120,
            "font.size": 10.0,
            "axes.titlesize": 11.5,
            "axes.titleweight": "bold",
            "axes.labelsize": 9.8,
            "axes.labelcolor": INK,
            "axes.edgecolor": "#B7C0C8",
            "axes.linewidth": 0.8,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelsize": 9.0,
            "ytick.labelsize": 9.0,
            "legend.fontsize": 8.8,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "grid.alpha": 0.85,
        }
    )


def polish_axes(axis, grid_axis: str = "y") -> None:
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    axis.set_axisbelow(True)
    axis.tick_params(length=0)


def add_header(fig, title: str, subtitle: str | None = None) -> None:
    fig.text(0.012, 0.965, title, ha="left", va="top", fontsize=13.4, weight="bold", color=INK)
    if subtitle:
        fig.text(
            0.012,
            0.902,
            subtitle,
            ha="left",
            va="top",
            fontsize=8.9,
            color="#52606C",
            linespacing=1.35,
        )


def add_footer(fig, text: str = "数据：2017 年清洗后 52,416 条 · 10 分钟采样") -> None:
    fig.text(0.988, 0.018, text, ha="right", va="bottom", fontsize=7.2, color="#7B8792")


def thousands(value, _position=None) -> str:
    return f"{value:,.0f}"


def compact(value: float) -> str:
    return f"{value / 1000:.1f}k"


def load_data() -> pd.DataFrame:
    frame = pd.read_csv(DATA, index_col="datetime", parse_dates=True)
    frame["hour"] = frame.index.hour
    frame["dow"] = frame.index.dayofweek
    frame["month"] = frame.index.month
    frame["date"] = frame.index.normalize()
    return frame


def daily_profile(frame: pd.DataFrame, out: Path) -> None:
    hourly = frame.groupby("hour")[[TOTAL, *ZONES.values()]].mean()
    peak_hour = int(hourly[TOTAL].idxmax())
    valley_hour = int(hourly[TOTAL].idxmin())
    peak = float(hourly.loc[peak_hour, TOTAL])
    valley = float(hourly.loc[valley_hour, TOTAL])

    fig, axis = plt.subplots(figsize=(8.6, 4.15))
    fig.subplots_adjust(left=0.105, right=0.985, top=0.79, bottom=0.15)
    axis.axvspan(12, 14, color=SOFT_BLUE, zorder=0)
    axis.plot(hourly.index, hourly[TOTAL], color=NAVY, linewidth=3.0, label="总负荷", zorder=4)
    for label, column, color in zip(ZONES, ZONES.values(), ZONE_COLORS):
        axis.plot(hourly.index, hourly[column], color=color, linewidth=1.8, alpha=0.92, label=label)

    axis.scatter([peak_hour], [peak], s=45, color=BRICK, edgecolor="white", linewidth=1.0, zorder=6)
    axis.scatter([valley_hour], [valley], s=45, color=NAVY, edgecolor="white", linewidth=1.0, zorder=6)
    axis.annotate(
        f"主峰 {peak_hour}:00\n{peak:,.0f} kW",
        xy=(peak_hour, peak),
        xytext=(16.5, 103000),
        textcoords="data",
        fontsize=9.3,
        color=BRICK,
        ha="left",
        arrowprops=dict(arrowstyle="-", color=BRICK, lw=1.0, alpha=0.7),
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#E5D6D2", lw=0.8, alpha=0.95),
    )
    axis.annotate(
        f"谷值 {valley_hour}:00\n{valley:,.0f} kW",
        xy=(valley_hour, valley),
        xytext=(0.9, 70500),
        textcoords="data",
        fontsize=9.3,
        color=NAVY,
        ha="left",
        arrowprops=dict(arrowstyle="-", color=NAVY, lw=1.0, alpha=0.65),
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#D8E1E9", lw=0.8, alpha=0.95),
    )
    axis.text(13, 79200, "午间平台", ha="center", va="bottom", fontsize=9.5, color=NAVY)
    axis.set_xlim(0, 23)
    axis.set_ylim(0, 108000)
    axis.set_xticks(range(0, 24, 2))
    axis.set_xlabel("小时")
    axis.set_ylabel("平均负荷（kW）")
    axis.yaxis.set_major_formatter(FuncFormatter(thousands))
    axis.legend(loc="upper left", ncol=2, frameon=False, handlelength=2.2, columnspacing=1.5)
    polish_axes(axis)
    add_header(
        fig,
        "日内负荷：06:00 谷值，20:00 主峰",
        f"2017 年可观测样本按小时平均；阴影为 12—14 时午间平台；峰谷比 {peak / valley:.2f}",
    )
    add_footer(fig)
    fig.savefig(out / "figA_daily_profile.png", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def weekly_profile(frame: pd.DataFrame, out: Path) -> None:
    labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekly = frame.groupby("dow")[[TOTAL, *ZONES.values()]].mean().reindex(range(7))
    weekday = float(weekly.loc[:4, TOTAL].mean())
    weekend = float(weekly.loc[5:, TOTAL].mean())

    zone_ratio = []
    for column in ZONES.values():
        zone_ratio.append(float(weekly.loc[5:, column].mean() / weekly.loc[:4, column].mean()))

    fig, axes = plt.subplots(1, 2, figsize=(8.9, 3.85), gridspec_kw={"width_ratios": [1.36, 1.0]})
    fig.subplots_adjust(left=0.085, right=0.985, top=0.76, bottom=0.15, wspace=0.28)

    bar_colors = [NAVY] * 5 + [WEEKEND] * 2
    axes[0].axvspan(4.5, 6.5, color="#FBF5EF", zorder=0)
    axes[0].set_xlim(-0.55, 6.55)
    bars = axes[0].bar(labels, weekly[TOTAL], color=bar_colors, width=0.66, zorder=3)
    for bar, value in zip(bars, weekly[TOTAL]):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            value + 240,
            f"{value:,.0f}",
            ha="center",
            va="bottom",
            fontsize=8.6,
            color=INK,
        )
    axes[0].set_ylim(62000, 74500)
    axes[0].set_ylabel("平均负荷（kW）")
    axes[0].set_title("(a) 周内日均总负荷", loc="left", pad=10)
    axes[0].yaxis.set_major_formatter(FuncFormatter(thousands))
    axes[0].legend(
        handles=[Patch(facecolor=NAVY, label="工作日"), Patch(facecolor=WEEKEND, label="周末")],
        loc="upper right",
        frameon=False,
    )
    polish_axes(axes[0])

    x = np.arange(3)
    ratio_bars = axes[1].bar(x, zone_ratio, color=ZONE_COLORS, width=0.58, zorder=3)
    axes[1].axhline(1.0, color="#7C8792", linestyle=(0, (4, 3)), linewidth=1.0, zorder=2)
    for bar, value in zip(ratio_bars, zone_ratio):
        delta = (value - 1) * 100
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.006,
            f"{value:.3f}\n({delta:+.1f}%)",
            ha="center",
            va="bottom",
            fontsize=8.6,
            color=INK,
        )
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(list(ZONES))
    axes[1].set_ylim(0.86, 1.045)
    axes[1].set_ylabel("周末均值 / 工作日均值")
    axes[1].set_title("(b) 分区周末效应", loc="left", pad=10)
    polish_axes(axes[1])

    add_header(
        fig,
        "周内规律：总量只低 3.8%，但 Zone2 的周末降幅达到 8.2%",
        f"工作日均值 {weekday:,.0f} kW，周末均值 {weekend:,.0f} kW；虚线为 1.00 基准；左图纵轴自 62,000 kW 起",
    )
    add_footer(fig)
    fig.savefig(out / "figB_weekly_profile.png", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def seasonal_profile(frame: pd.DataFrame, out: Path) -> None:
    monthly = frame.groupby("month")[[TOTAL, *ZONES.values()]].mean()
    seasons = ["春季", "夏季", "秋季", "冬季"]
    month_to_season = {12: "冬季", 1: "冬季", 2: "冬季", 3: "春季", 4: "春季", 5: "春季", 6: "夏季", 7: "夏季", 8: "夏季", 9: "秋季", 10: "秋季", 11: "秋季"}
    frame = frame.copy()
    frame["season"] = frame["month"].map(month_to_season)
    seasonal = frame.groupby("season")[[TOTAL, *ZONES.values()]].mean().reindex(seasons)

    fig, axes = plt.subplots(1, 2, figsize=(8.9, 3.85), gridspec_kw={"width_ratios": [1.16, 1.0]})
    fig.subplots_adjust(left=0.09, right=0.985, top=0.76, bottom=0.15, wspace=0.28)

    axes[0].axvspan(6, 8, color=SOFT_ORANGE, zorder=0)
    axes[0].plot(monthly.index, monthly[TOTAL], color=NAVY, linewidth=2.8, marker="o", markersize=4.5, label="总负荷", zorder=4)
    for label, column, color in zip(ZONES, ZONES.values(), ZONE_COLORS):
        axes[0].plot(monthly.index, monthly[column], color=color, linewidth=1.6, marker="o", markersize=3.0, label=label, alpha=0.92)
    axes[0].text(8.55, 90500, "夏季", ha="left", va="center", fontsize=9.0, color=ORANGE)
    july = float(monthly.loc[7, TOTAL])
    axes[0].annotate(
        f"{july:,.0f}",
        xy=(7, july),
        xytext=(-14, 12),
        textcoords="offset points",
        ha="right",
        va="bottom",
        fontsize=8.5,
        color=NAVY,
    )
    december = float(monthly.loc[12, TOTAL])
    axes[0].annotate(
        f"{december:,.0f}",
        xy=(12, december),
        xytext=(1, 10),
        textcoords="offset points",
        ha="center",
        fontsize=8.5,
        color=NAVY,
    )
    axes[0].set_xticks(range(1, 13))
    axes[0].set_xlim(0.5, 12.5)
    axes[0].set_ylim(0, 99000)
    axes[0].set_xlabel("月份")
    axes[0].set_ylabel("平均负荷（kW）")
    axes[0].set_title("(a) 月度平均负荷", loc="left", pad=10)
    axes[0].yaxis.set_major_formatter(FuncFormatter(thousands))
    axes[0].legend(
        loc="center left",
        bbox_to_anchor=(0.02, 0.52),
        ncol=2,
        frameon=False,
        columnspacing=1.0,
        handlelength=1.6,
    )
    polish_axes(axes[0])

    x = np.arange(len(seasons))
    width = 0.25
    for index, (label, column, color) in enumerate(zip(ZONES, ZONES.values(), ZONE_COLORS)):
        axes[1].bar(x + (index - 1) * width, seasonal[column], width, color=color, label=label, zorder=3)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(seasons)
    axes[1].set_ylim(0, 41000)
    axes[1].set_ylabel("平均负荷（kW）")
    axes[1].set_title("(b) 季度平均负荷（分区）", loc="left", pad=10)
    axes[1].yaxis.set_major_formatter(FuncFormatter(thousands))
    axes[1].legend(
        loc="upper right",
        ncol=3,
        frameon=False,
        handlelength=1.1,
        columnspacing=0.7,
        fontsize=8.3,
    )
    polish_axes(axes[1])

    summer = float(seasonal.loc["夏季", TOTAL])
    year_mean = float(frame[TOTAL].mean())
    add_header(
        fig,
        "季节规律：夏季单峰，冬季与春秋接近",
        f"夏季均值 {summer:,.0f} kW，比全年高 {(summer / year_mean - 1) * 100:.1f}%；7 月最高、12 月最低",
    )
    add_footer(fig)
    fig.savefig(out / "figC_seasonal_profile.png", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def zone_boxplot(frame: pd.DataFrame, out: Path) -> None:
    data = [frame[column].to_numpy() for column in ZONES.values()]
    shares = [frame[column].mean() / frame[TOTAL].mean() * 100 for column in ZONES.values()]
    medians = [float(np.median(values)) for values in data]

    fig, axis = plt.subplots(figsize=(8.6, 3.8))
    fig.subplots_adjust(left=0.115, right=0.80, top=0.715, bottom=0.18)
    box = axis.boxplot(
        data,
        orientation="horizontal",
        widths=0.56,
        patch_artist=True,
        showfliers=False,
        whis=1.5,
        medianprops=dict(color="white", linewidth=2.0),
        whiskerprops=dict(color="#65727D", linewidth=1.0),
        capprops=dict(color="#65727D", linewidth=1.0),
    )
    for patch, color in zip(box["boxes"], ZONE_COLORS):
        patch.set_facecolor(color)
        patch.set_edgecolor(color)
        patch.set_alpha(0.88)
    axes_means = [float(values.mean()) for values in data]
    positions = np.arange(1, 4)
    axis.scatter(axes_means, positions, marker="D", s=28, color="white", edgecolor=INK, linewidth=0.8, zorder=6)

    axis.set_yticks(positions)
    axis.set_yticklabels(list(ZONES))
    axis.invert_yaxis()
    axis.set_xlim(0, 54500)
    axis.set_xlabel("负荷（kW）")
    axis.xaxis.set_major_formatter(FuncFormatter(thousands))
    for position, median, share in zip(positions, medians, shares):
        axis.text(
            1.015,
            position,
            f"中位数 {median:,.0f} kW\n占比 {share:.1f}%",
            transform=axis.get_yaxis_transform(),
            ha="left",
            va="center",
            fontsize=8.6,
            color=MUTED,
            linespacing=1.35,
        )
    polish_axes(axis, grid_axis="x")
    add_header(
        fig,
        "分区负荷分布：规模与离散度差异明显",
        "箱体为四分位区间，白线为中位数，菱形为均值，须线为 1.5×IQR\n须线外极端值未逐点绘制；右侧标注中位数与全年占比",
    )
    add_footer(fig)
    fig.savefig(out / "figD_zone_boxplot.png", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def zone_metrics(frame: pd.DataFrame, out: Path) -> None:
    means = np.array([frame[column].mean() for column in ZONES.values()])
    shares = means / frame[TOTAL].mean() * 100
    cv = np.array([frame[column].std() / frame[column].mean() for column in ZONES.values()])
    hourly = frame.groupby("hour")[list(ZONES.values())].mean()
    pvr = np.array([hourly[column].max() / hourly[column].min() for column in ZONES.values()])

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(9.0, 3.7),
        gridspec_kw={"width_ratios": [1.24, 0.82, 0.82]},
    )
    fig.subplots_adjust(left=0.125, right=0.985, top=0.76, bottom=0.16, wspace=0.46)

    y = np.arange(3)
    bars = axes[0].barh(y, means, color=ZONE_COLORS, height=0.56, zorder=3)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(list(ZONES))
    axes[0].invert_yaxis()
    axes[0].set_xlim(0, 42000)
    axes[0].set_xlabel("平均负荷（kW）")
    axes[0].xaxis.set_major_formatter(FuncFormatter(thousands))
    axes[0].set_title("(a) 规模与占比", loc="left", pad=10)
    for bar, value, share in zip(bars, means, shares):
        axes[0].text(
            value + 500,
            bar.get_y() + bar.get_height() / 2,
            f"{value:,.0f} kW\n占比 {share:.1f}%",
            va="center",
            ha="left",
            fontsize=8.6,
            color=INK,
            linespacing=1.35,
        )
    polish_axes(axes[0], grid_axis="x")

    x = np.arange(3)
    panels = [
        (axes[1], cv, 0.45, "(b) 变异系数"),
        (axes[2], pvr, 2.55, "(c) 峰谷比"),
    ]
    for axis, values, upper, title in panels:
        axis.bar(x, values, color=ZONE_COLORS, width=0.60, zorder=3)
        for xpos, value in zip(x, values):
            axis.text(
                xpos,
                value + upper * 0.025,
                f"{value:.2f}",
                ha="center",
                va="bottom",
                fontsize=8.7,
                color=INK,
            )
        axis.set_xticks(x)
        axis.set_xticklabels(list(ZONES))
        axis.set_ylim(0, upper)
        axis.set_title(title, loc="left", pad=10)
        polish_axes(axis)

    add_header(
        fig,
        "分区规模与波动性",
        "Zone1 规模最大；Zone3 变异系数 0.37、峰谷比 2.23，均为最高，波动最强",
    )
    add_footer(fig)
    fig.savefig(out / "figE_zone_metrics.png", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def zone3_ratio(frame: pd.DataFrame, out: Path) -> None:
    monthly = frame.groupby("month")[list(ZONES.values())].mean()
    ratio = monthly[ZONES["Zone3"]] / monthly[ZONES["Zone1"]]

    fig, axis = plt.subplots(figsize=(8.4, 3.75))
    fig.subplots_adjust(left=0.115, right=0.98, top=0.76, bottom=0.18)
    axis.axvspan(7, 12, color=SOFT_ORANGE, zorder=0)
    axis.plot(ratio.index, ratio.values, color=BRICK, linewidth=2.4, marker="o", markersize=4.5, markerfacecolor="white", markeredgewidth=1.4, zorder=4)
    for month, dx, dy, align in [(7, 0, 13, "center"), (9, -9, 10, "right"), (12, -2, 15, "right")]:
        value = float(ratio.loc[month])
        axis.annotate(
            f"{value:.3f}",
            xy=(month, value),
            xytext=(dx, dy),
            textcoords="offset points",
            ha=align,
            fontsize=8.8,
            color=INK,
        )
    axis.annotate(
        "11 月回升",
        xy=(11, ratio.loc[11]),
        xytext=(0, -15),
        textcoords="offset points",
        ha="center",
        va="top",
        fontsize=7.9,
        color=MUTED,
    )
    axis.set_xticks(range(1, 13))
    axis.set_xlim(0.6, 12.5)
    axis.set_ylim(0.34, 0.89)
    axis.set_xlabel("月份")
    axis.set_ylabel("Zone3 / Zone1")
    axis.text(
        0.015,
        0.965,
        "7 月 0.787 → 12 月 0.381（−51.6%）",
        transform=axis.transAxes,
        ha="left",
        va="top",
        fontsize=8.8,
        color=INK,
        bbox=dict(boxstyle="round,pad=0.38", fc="white", ec="#E3D6D2", lw=0.8),
    )
    polish_axes(axis)
    add_header(fig, "Zone3 的结构变化：相对规模持续收缩", "月度均值之比；保留 11 月回升，不用离群点规则抹平")
    add_footer(fig)
    fig.savefig(out / "figF_zone3_ratio.png", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def weather_heatmap(frame: pd.DataFrame, out: Path) -> None:
    weather = {
        "temperature": "温度",
        "humidity": "湿度",
        "wind_speed": "风速",
        "general_diffuse_flows": "散射辐照（总）",
        "diffuse_flows": "散射辐照（直）",
        **{column: label for label, column in ZONES.items()},
    }
    weather[TOTAL] = "总负荷"
    columns = list(weather)
    corr = frame[columns].corr(method="pearson")

    cmap = LinearSegmentedColormap.from_list(
        "report_diverging",
        ["#24527A", "#6F9DB7", "#F4F1EA", "#D89A7E", "#9E3F3C"],
    )
    fig, axis = plt.subplots(figsize=(7.4, 5.9))
    fig.subplots_adjust(left=0.21, right=0.895, top=0.80, bottom=0.19)
    image = axis.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1, aspect="equal")
    labels = [weather[column] for column in columns]
    axis.set_xticks(range(len(columns)))
    axis.set_yticks(range(len(columns)))
    axis.set_xticklabels(labels, rotation=38, ha="right", fontsize=8.7)
    axis.set_yticklabels(labels, fontsize=8.7)
    axis.set_xticks(np.arange(-0.5, len(columns), 1), minor=True)
    axis.set_yticks(np.arange(-0.5, len(columns), 1), minor=True)
    axis.grid(which="minor", color="white", linewidth=1.2)
    axis.tick_params(which="minor", bottom=False, left=False)
    axis.tick_params(which="major", length=0)
    for boundary in [4.5]:
        axis.axhline(boundary, color="white", linewidth=2.4, zorder=4)
        axis.axvline(boundary, color="white", linewidth=2.4, zorder=4)
    axis.text(
        0.25,
        1.035,
        "气象变量",
        transform=axis.transAxes,
        ha="center",
        va="bottom",
        fontsize=9.0,
        weight="bold",
        color=MUTED,
    )
    axis.text(
        0.82,
        1.035,
        "负荷变量",
        transform=axis.transAxes,
        ha="center",
        va="bottom",
        fontsize=9.0,
        weight="bold",
        color=MUTED,
    )
    for row in range(len(columns)):
        for column in range(len(columns)):
            value = corr.iloc[row, column]
            display = 0.0 if abs(value) < 0.005 else value
            axis.text(
                column,
                row,
                f"{display:.2f}",
                ha="center",
                va="center",
                fontsize=7.6,
                color="white" if abs(value) > 0.52 else INK,
            )
    colorbar = fig.colorbar(image, ax=axis, fraction=0.035, pad=0.025)
    colorbar.set_label("Pearson r", color=INK, fontsize=9.5)
    colorbar.ax.tick_params(labelsize=8.5, length=0)
    colorbar.outline.set_visible(False)
    add_header(
        fig,
        "气象与负荷的全样本相关结构",
        "Pearson 相关系数；白线分隔气象与负荷两组；对角线为 1.00，矩阵关于对角线镜像",
    )
    add_footer(fig)
    fig.savefig(out / "figG_corr_heatmap.png", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def monthly_correlation(frame: pd.DataFrame, out: Path) -> None:
    rows = []
    for month in range(1, 13):
        subset = frame[frame["month"] == month]
        rows.append(
            {
                "month": month,
                "total": subset["temperature"].corr(subset[TOTAL]),
                **{
                    label: subset["temperature"].corr(subset[column])
                    for label, column in ZONES.items()
                },
            }
        )
    monthly = pd.DataFrame(rows).set_index("month")

    fig, axis = plt.subplots(figsize=(8.6, 3.8))
    fig.subplots_adjust(left=0.11, right=0.985, top=0.77, bottom=0.16)
    axis.axvspan(5.5, 8.5, color=SOFT_ORANGE, zorder=0)
    axis.plot(
        monthly.index,
        monthly["total"],
        color=NAVY,
        linewidth=2.7,
        marker="o",
        markersize=4.6,
        label="总负荷",
        zorder=5,
    )
    for label, color, line_style, marker in zip(
        ZONES,
        ZONE_COLORS,
        ["-", "--", ":"],
        ["s", "^", "D"],
    ):
        axis.plot(
            monthly.index,
            monthly[label],
            color=color,
            linewidth=1.5,
            linestyle=line_style,
            marker=marker,
            markersize=3.3,
            markerfacecolor="white",
            markeredgewidth=1.0,
            label=label,
            zorder=4,
        )
    axis.text(7, 0.605, "夏季", ha="center", va="top", fontsize=8.8, color=ORANGE)
    axis.text(
        0.99,
        0.95,
        "12 个月均为正相关",
        transform=axis.transAxes,
        ha="right",
        va="top",
        fontsize=8.8,
        color=INK,
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#DDE3E8", lw=0.8),
    )
    axis.set_xticks(range(1, 13))
    axis.set_xlim(0.45, 12.55)
    axis.set_ylim(0, 0.63)
    axis.set_yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    axis.set_xlabel("月份")
    axis.set_ylabel("温度-负荷 Pearson r")
    axis.legend(
        loc="upper left",
        ncol=2,
        frameon=False,
        handlelength=2.0,
        columnspacing=1.6,
        labelspacing=0.45,
    )
    polish_axes(axis)
    add_header(
        fig,
        "温度效应：方向稳定为正，强度随时段与季节变化",
        "月相关范围 0.194—0.509，7 月最高；阴影为夏季；相关不等于因果",
    )
    add_footer(fig)
    fig.savefig(out / "figH_temp_corr_by_month.png", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def month_hour_heatmap(frame: pd.DataFrame, out: Path) -> None:
    pivot = pd.DataFrame(index=range(1, 13), columns=range(24), dtype=float)
    for month in range(1, 13):
        for hour in range(24):
            subset = frame[(frame["month"] == month) & (frame["hour"] == hour)]
            if len(subset) > 5:
                pivot.loc[month, hour] = subset["temperature"].corr(subset[TOTAL])

    cmap = LinearSegmentedColormap.from_list(
        "report_diverging",
        ["#24527A", "#6F9DB7", "#F4F1EA", "#D89A7E", "#9E3F3C"],
    )
    fig, (axis, count_axis) = plt.subplots(
        1,
        2,
        figsize=(9.0, 4.35),
        gridspec_kw={"width_ratios": [1.0, 0.27]},
    )
    fig.subplots_adjust(left=0.10, right=0.955, top=0.75, bottom=0.17, wspace=0.32)
    image = axis.imshow(pivot.values, cmap=cmap, vmin=-0.6, vmax=0.6, aspect="auto")
    axis.set_xticks(range(0, 24, 2))
    axis.set_xticklabels([f"{hour:02d}" for hour in range(0, 24, 2)])
    axis.set_yticks(range(12))
    axis.set_yticklabels([f"{month}月" for month in range(1, 13)])
    axis.set_xlabel("小时")
    axis.set_ylabel("月份")
    axis.tick_params(length=0)
    axis.vlines(
        np.arange(0.5, 24, 1), -0.5, 11.5, color="white", linewidth=0.35, alpha=0.32, zorder=2
    )
    axis.hlines(
        np.arange(0.5, 12, 1), -0.5, 23.5, color="white", linewidth=0.35, alpha=0.32, zorder=2
    )
    for boundary in [2.5, 5.5, 8.5, 11.5]:
        axis.axhline(boundary, color="white", linewidth=1.4, alpha=0.95, zorder=3)
    colorbar = fig.colorbar(image, ax=axis, fraction=0.028, pad=0.018)
    colorbar.set_label("Pearson r", color=INK, fontsize=9.5)
    colorbar.set_ticks([-0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6])
    colorbar.ax.tick_params(labelsize=8.5, length=0)
    colorbar.outline.set_visible(False)

    negative_by_month = (pivot < 0).sum(axis=1).to_numpy()
    count_axis.barh(
        np.arange(12),
        negative_by_month,
        height=0.62,
        color=BRICK,
        alpha=0.88,
        zorder=3,
    )
    for position, count in enumerate(negative_by_month):
        count_axis.text(
            count + 0.9,
            position,
            f"{int(count)}",
            ha="left",
            va="center",
            fontsize=9.8,
            color=INK if count > 0 else "#8B969F",
            fontweight="bold" if count >= 20 else "normal",
        )
    count_axis.set_xlim(0, 28)
    count_axis.set_ylim(11.5, -0.5)
    count_axis.set_xticks([0, 6, 12, 18, 24])
    count_axis.set_yticks([])
    count_axis.set_xlabel("负相关小时数")
    count_axis.set_title("(b) 各月负相关小时数", loc="left", pad=10, fontsize=11.5)
    polish_axes(count_axis, grid_axis="x")
    count_axis.spines["left"].set_visible(False)
    axis.set_title("(a) 月×小时相关系数", loc="left", pad=10, fontsize=11.5)

    negative = int((pivot < 0).sum().sum())
    add_header(
        fig,
        "温度效应的时段差异：局部负相关不可忽略",
        f"288 个月×小时切片中 {negative} 个为负（蓝色）；色标截断于 ±0.6；白色横线分隔季节",
    )
    add_footer(fig)
    fig.savefig(out / "figI_temp_corr_month_hour.png", bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="overwrite figures/patterns")
    parser.add_argument("--out", type=Path, help="write figures to this directory")
    arguments = parser.parse_args()

    configure()
    frame = load_data()
    target = arguments.out or (FIG_DIR if arguments.apply else PREVIEW_DIR)
    target.mkdir(parents=True, exist_ok=True)
    daily_profile(frame, target)
    weekly_profile(frame, target)
    seasonal_profile(frame, target)
    zone_boxplot(frame, target)
    zone_metrics(frame, target)
    zone3_ratio(frame, target)
    weather_heatmap(frame, target)
    monthly_correlation(frame, target)
    month_hour_heatmap(frame, target)
    print(f"figures written to {target}")


if __name__ == "__main__":
    main()
