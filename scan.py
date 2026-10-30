"""Scan the default-branch history of popular open-source repos for commits carrying an AI coding tool's signature.

For every non-merge commit since 2025-01-01 we read the author and the Co-authored-by trailers, plus the message body,
and classify it as:
  automation : authored by a classic bot (dependabot, renovate, CI/release/merge bots) with no AI signature
  ai_author  : the AI tool is the commit author (an agent wrote the change, e.g. Copilot coding agent, Cursor agent)
  ai_coauthor: a human is the author and an AI tool is credited as co-author (e.g. Claude Code's trailer)
  human      : everything else (which includes AI use that left no signature)
"""
import re, subprocess, json, glob, os, collections

AI = [  # (family, regex on "name <email>")
    ("Copilot", r"\+copilot@users\.noreply\.github\.com|<copilot@github\.com>|copilot-swe-agent|copilot autofix|github-advanced-security\[bot\]"),
    ("Claude", r"robobun@oven\.sh|noreply@anthropic\.com|claude\[bot\]|claude-bot@|electron-claude\[bot\]|svc-devxp-claude@|<claude@anthropic\.ai>"),
    ("Cursor", r"cursoragent@cursor\.com|cursor\[bot\]"),
    ("Codex", r"noreply@openai\.com|<codex@openai\.com>|chatgpt-codex-connector"),
    ("Gemini", r"gemini-code-assist\[bot\]"),
    ("Other agents", r"google-labs-jules\[bot\]|amp@ampcode\.com|factory-droid\[bot\]|devin-ai-integration|openhands@all-hands\.dev|\(aider\)"),
]
AI_RE = [(f, re.compile(p, re.I)) for f, p in AI]
BODY_RE = re.compile(r"Generated with \[?Claude Code|Co-authored-by: Claude", re.I)
BOT_RE = re.compile(r"\[bot\]|\bbot\b|mergebot|updatebot|robot|automation|cronjob|lock file bot|release bot", re.I)

SEP, END = "\x1f", "\x1e"
FMT = SEP.join(["%cs", "%an <%ae>", "%(trailers:key=Co-authored-by,valueonly,separator=%x1d)", "%b"]) + END

def family(s):
    for f, r in AI_RE:
        if r.search(s):
            return f
    return None

rows = []
for path in sorted(glob.glob("repos/*.git")):
    repo = os.path.basename(path)[:-4].replace("_", "/", 1)
    out = subprocess.run(["git", "-C", path, "log", "--no-merges", "--since=2025-01-01", "--until=2026-10-31", f"--format={FMT}"],
                         capture_output=True, text=True, errors="replace").stdout
    for rec in out.split(END):
        rec = rec.strip("\n")
        if not rec:
            continue
        parts = rec.split(SEP)
        if len(parts) < 4:
            continue
        date, author, coauth, body = parts[0], parts[1], parts[2], SEP.join(parts[3:])
        coauthors = [c.strip() for c in coauth.split("\x1d") if c.strip()]
        fa = family(author)
        fc = next((family(c) for c in coauthors if family(c)), None)
        if fc is None and BODY_RE.search(body):
            fc = "Claude"
        if fa:
            kind, fam = "ai_author", fa
        elif fc:
            kind, fam = "ai_coauthor", fc
        elif BOT_RE.search(author):
            kind, fam = "automation", None
        else:
            kind, fam = "human", None
        rows.append((repo, date[:7], kind, fam))

json.dump(rows, open("results/commits.json", "w"))
print(len(rows), "commits from", len({r[0] for r in rows}), "repos")
c = collections.Counter(k for *_, k, _ in rows); print(c)
