"""Monthly and per-repo shares of AI-signed commits from results/commits.json."""
import json, collections
import numpy as np
rows = json.load(open("results/commits.json"))
months = sorted({m for _, m, _, _ in rows if "2025-01" <= m <= "2026-10"})
repos = sorted({r for r, *_ in rows})
cnt = collections.defaultdict(collections.Counter)      # (repo, month) -> kind counts
fam = collections.defaultdict(collections.Counter)      # month -> family counts
for r, m, k, f in rows:
    cnt[(r, m)][k] += 1
    if f: fam[m][f] += 1

def share(c):
    hum = c["human"] + c["ai_author"] + c["ai_coauthor"]
    return (c["ai_author"] + c["ai_coauthor"]) / hum if hum else None

pooled, median, q75, any_ai = [], [], [], []
for m in months:
    tot = collections.Counter()
    per = []
    n_with = 0
    for r in repos:
        c = cnt[(r, m)]; tot.update(c)
        s = share(c)
        if s is not None and (c["human"] + c["ai_author"] + c["ai_coauthor"]) >= 20:
            per.append(s); n_with += s > 0
    pooled.append(share(tot)); median.append(float(np.median(per))); q75.append(float(np.percentile(per, 75)))
    any_ai.append(n_with / len(per))
recent = ["2026-07", "2026-08", "2026-09"]
per_repo = {}
for r in repos:
    c = collections.Counter()
    for m in recent: c.update(cnt[(r, m)])
    hum = c["human"] + c["ai_author"] + c["ai_coauthor"]
    if hum >= 30:
        per_repo[r] = {"share": share(c), "n": hum, "ai_author": c["ai_author"] / hum, "ai_coauthor": c["ai_coauthor"] / hum}
fam_share = {m: {f: v / max(1, sum(fam[m].values())) for f, v in fam[m].items()} for m in months}
tot_kinds = collections.Counter(k for _, m, k, _ in rows if m in recent)
R = {"months": months, "pooled": pooled, "median": median, "q75": q75, "share_repos_with_any_ai": any_ai,
     "per_repo_recent": dict(sorted(per_repo.items(), key=lambda kv: -kv[1]["share"])),
     "family_share": fam_share, "family_counts": {m: dict(fam[m]) for m in months},
     "recent_kinds": dict(tot_kinds), "n_commits": len(rows), "n_repos": len(repos)}
json.dump(R, open("results/results.json", "w"), indent=1)
for m, p, md, a in zip(months, pooled, median, any_ai): print(m, f"pooled {100*p:5.1f}%  median {100*md:5.1f}%  repos with any {100*a:3.0f}%")
print("recent kinds", tot_kinds)
for r, v in list(R["per_repo_recent"].items()):
    print(f"{r:35s} {100*v['share']:5.1f}%  author {100*v['ai_author']:4.1f}%  n={v['n']}")
