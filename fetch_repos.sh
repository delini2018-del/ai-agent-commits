#!/usr/bin/env bash
# Download the main-branch history (no file contents) of every repo in repos.txt since 2025-01-01
set -e
mkdir -p repos
while read -r r; do
  n=$(echo "$r" | tr / _)
  [ -d "repos/$n.git" ] || git clone -q --bare --filter=blob:none --shallow-since=2025-01-01 "https://github.com/$r.git" "repos/$n.git"
done < repos.txt
