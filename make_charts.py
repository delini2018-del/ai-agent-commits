"""Draw the article's figures from results/results.json and results/commits.json."""
import json, collections
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = json.load(open("results/results.json"))
INK, INK2, GRID, BG = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
BLUE, ORANGE, AQUA, YELLOW, MAG = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": INK2, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "figure.facecolor": BG, "axes.facecolor": BG})

def title(fig, t, sub, y=0.965):
    fig.text(0.02, y, t, ha="left", va="top", fontsize=15, color=INK, weight="bold")
    fig.text(0.02, y - 0.06 * (0.965 / y if y < 0.965 else 1), sub, ha="left", va="top", fontsize=11, color=INK2)

M = R["months"]; x = np.arange(len(M))
lab = [m[2:4] + "/" + m[5:] if m[5:] in ("01", "04", "07", "10") else "" for m in M]
lab = [("Jan\n2025" if m == "2025-01" else "Apr" if m.endswith("04") else "Jul" if m.endswith("07") else "Oct" if m.endswith("10") else "Jan\n2026" if m == "2026-01" else "") for m in M]

# ---------- 1: monthly share vs GitHub's headline ----------
fig, ax = plt.subplots(figsize=(11, 5.6))
ax.plot(x, [100 * v for v in R["pooled"]], color=BLUE, lw=2.4, label="All 55 projects pooled (big projects count more)")
ax.plot(x, [100 * v for v in R["median"]], color=AQUA, lw=2.4, label="The typical project (median)")
i_mar, i_sep = M.index("2026-03"), M.index("2026-09")
ax.plot([i_mar, i_sep], [17, 40], ls="--", color=ORANGE, lw=1.6)
ax.plot([i_mar, i_sep], [17, 40], "D", color=ORANGE, ms=9, label="GitHub Octoverse: PRs whose first draft came from an agent")
ax.text(i_sep - 0.3, 41.5, "40%", color=ORANGE, ha="right", fontsize=11, weight="bold")
ax.text(i_mar - 0.3, 18.5, "17%", color=ORANGE, ha="right", fontsize=11, weight="bold")
ax.text(len(M) - 1 + 0.25, 100 * R["pooled"][-1], f"{100 * R['pooled'][-1]:.0f}%", color=BLUE, va="center", fontsize=11)
ax.text(i_sep + 0.25, 100 * R["median"][i_sep] - 2, f"{100 * R['median'][i_sep]:.0f}%", color=AQUA, va="center", fontsize=11)
ax.text(len(M) - 1, 100 * R["pooled"][-1] - 5, "Oct: partial\nmonth", color=INK2, fontsize=9, ha="center")
ax.set_xticks(x, lab); ax.set_xlim(-0.5, len(M) + 0.6); ax.set_ylim(0, 50)
ax.set_ylabel("Commits carrying an AI tool's signature (%)"); ax.grid(axis="y", color=GRID)
ax.legend(frameon=False, loc="upper left", fontsize=10)
title(fig, "Agents start 40% of pull requests. In big open-source projects, far less code lands",
      "Share of human and AI commits on the main branch of 55 popular repos that credit an AI tool, by month")
fig.subplots_adjust(top=0.84, left=0.08, right=0.95, bottom=0.12)
fig.savefig("charts/01_monthly_share.png", dpi=200); plt.close(fig)

# ---------- 2: per-repo share, Jul-Sep 2026 ----------
P = R["per_repo_recent"]; names = list(P); vals = [100 * P[n]["share"] for n in names]
auth = [100 * P[n]["ai_author"] for n in names]
fig, ax = plt.subplots(figsize=(11, 13))
y = np.arange(len(names))
ax.barh(y, [v - a for v, a in zip(vals, auth)], left=auth, color=BLUE, height=0.7, label="AI credited as co-author")
ax.barh(y, auth, color=ORANGE, height=0.7, label="AI is the commit author (agent)")
for yi, v in zip(y, vals):
    ax.text(v + 0.8, yi, f"{v:.0f}%" if v >= 1 else ("0%" if v == 0 else "<1%"), va="center", fontsize=9, color=INK)
ax.set_yticks(y, names, fontsize=9); ax.invert_yaxis(); ax.set_xlim(0, 90)
ax.set_xlabel("Commits crediting an AI tool, July–September 2026 (%)"); ax.grid(axis="x", color=GRID); ax.set_axisbelow(True)
ax.legend(frameon=False, loc="lower right", fontsize=10)
fig.text(0.02, 0.985, "A handful of projects are mostly AI. Most are barely touched", ha="left", va="top", fontsize=15, color=INK, weight="bold")
fig.text(0.02, 0.968, "Per-repo share of human and AI commits that carry an AI tool's signature (repos with at least 30 commits)", ha="left", va="top", fontsize=11, color=INK2)
fig.subplots_adjust(top=0.95, left=0.27, right=0.97, bottom=0.05)
fig.savefig("charts/02_per_repo.png", dpi=200); plt.close(fig)

# ---------- 3: concentration ----------
rows = json.load(open("results/commits.json"))
c = collections.Counter(r[0] for r in rows if "2026-07" <= r[1] <= "2026-09" and r[2] in ("ai_author", "ai_coauthor"))
counts = [v for _, v in c.most_common()]; tot = sum(counts)
cum = np.concatenate([[0], np.cumsum(counts) / tot * 100])
fig, ax = plt.subplots(figsize=(11, 5.2))
ax.plot(np.arange(len(cum)), cum, color=BLUE, lw=2.4, marker="o", ms=5, mec=BG)
for k in (5, 10):
    ax.plot([k], [cum[k]], "o", ms=10, color=ORANGE, mec=BG, mew=2)
    ax.annotate(f"top {k} projects: {cum[k]:.0f}% of all\nAI-signed commits", (k, cum[k]), xytext=(18, -38), textcoords="offset points", fontsize=10.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
ax.set_xlim(0, len(cum) - 1 + 1); ax.set_ylim(0, 105)
ax.set_xlabel("Projects, ranked by number of AI-signed commits"); ax.set_ylabel("Cumulative share of AI-signed commits (%)")
ax.grid(axis="y", color=GRID)
title(fig, "The AI code is concentrated in a few places",
      f"{tot:,} AI-signed commits across the 55 projects, July–September 2026")
fig.subplots_adjust(top=0.84, left=0.08, right=0.97, bottom=0.12)
fig.savefig("charts/03_concentration.png", dpi=200); plt.close(fig)

# ---------- 4: tool mix over time ----------
FC = R["family_counts"]
fams = [("Claude", ORANGE), ("Copilot", BLUE), ("Cursor", AQUA), ("Codex", YELLOW)]
fig, ax = plt.subplots(figsize=(11, 5.2))
for f, col in fams:
    v = [FC[m].get(f, 0) for m in M]
    ax.plot(x, v, color=col, lw=2.2, label=f)
    ax.text(len(M) - 1 + 0.25, v[-2] if f in ("Codex",) else v[-1], f, color=col, va="center", fontsize=10.5)
oth = [sum(n for k, n in FC[m].items() if k not in dict(fams)) for m in M]
ax.plot(x, oth, color=INK2, lw=1.6, ls=":", label="Gemini, Jules, Amp, Devin and others")
ax.set_xticks(x, lab); ax.set_xlim(-0.5, len(M) + 1.2)
ax.set_ylabel("AI-signed commits per month"); ax.grid(axis="y", color=GRID)
ax.legend(frameon=False, loc="upper left", fontsize=10)
title(fig, "Which AI tools leave their name on the code",
      "Monthly commits in the 55 projects carrying each tool's signature (October 2026 is a partial month)")
fig.subplots_adjust(top=0.84, left=0.08, right=0.93, bottom=0.12)
fig.savefig("charts/04_tools.png", dpi=200); plt.close(fig)
print("ok")
