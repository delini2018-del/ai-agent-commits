# ai-agent-commits

Code and results for the article **"AI Agents Now Open 40% of GitHub's Pull Requests. I Checked How Much Code Actually Gets In."**

GitHub's Octoverse (Oct 28, 2026) says more than 40% of pull requests started with an agent's first draft in September 2026.
This repo asks a narrower question: in 55 popular open-source projects, how many commits that landed on the main branch
carry an AI coding tool's signature (author or Co-authored-by)?

## Headline results (428,109 commits, Jan 2025 – Oct 30 2026)

- AI-signed share of human + AI commits, all projects pooled: 0% (Jan 2025) -> 5.4% (Jan 2026) -> 20.7% (Sep 2026) -> 24.1% (Oct 2026, to the 30th)
- Typical project (median) in Sep 2026: 4.2%
- Projects with at least one AI-signed commit in the month: 4% (Jan 2025) -> 73% (Sep 2026)
- Jul–Sep 2026: 7 of 51 projects above 40% (bun 78%, pandas 70%, cli/cli 69%, vscode 62%, dotnet/runtime 60%, n8n 49%, aspnetcore 47%); 9 at 0%; median 2.5%
- Top 5 projects = 72% of all AI-signed commits; top 10 = 90%
- 80% of AI-signed commits credit AI as co-author with a human author

## Run it

```bash
pip install -r requirements.txt
./fetch_repos.sh        # blobless clones of each repo's history since 2025 (about 1.3 GB)
python scan.py          # -> results/commits.json
python analyze.py       # -> results/results.json
python make_charts.py   # -> charts/*.png
```

Or open `ai_agent_commits.ipynb` in Google Colab. To scan your own repos, edit `repos.txt`.

## What counts as an AI signature

See the `AI` list in `scan.py`: Copilot bot accounts and noreply addresses, Claude (noreply@anthropic.com, claude[bot], Bun's
RoboBun bot), Cursor, Codex, Gemini Code Assist, Jules, Amp, Factory, Devin, OpenHands, aider, plus "Generated with Claude Code".

## Limits

Only signed AI use is visible, so all numbers are a floor. Squash-merge habits differ by project. The repo list is a convenience
sample of popular projects. This measures commits on main branches, not pull requests opened.

## Licence

MIT. See `LICENSE`.
