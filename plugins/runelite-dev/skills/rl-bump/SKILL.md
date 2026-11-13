---
name: rl-bump
description: Bump a plugin's commit in the RuneLite Plugin Hub and open the update PR.
argument-hint: <plugin-name>
disable-model-invocation: true
---

Bump `plugins/$ARGUMENTS` in the user's local clone of their `runelite/plugin-hub` fork to the plugin repo's latest pushed commit, then open a PR against `runelite/plugin-hub`. No argument: use the plugin the user names or has open.

## 0. Locate the checkout

- Find the clone: the current directory if it has a `plugins/` folder and a remote pointing at a `plugin-hub` repo, else a `plugin-hub` sibling of the current directory. Otherwise ask for the path.
- `origin` must be the user's fork. If no `upstream` remote exists, add it: `git remote add upstream https://github.com/runelite/plugin-hub.git`.
- Fork owner is the owner in the `origin` URL; it is used in step 6.

## 1. Resolve commits

- `git fetch upstream`. Read `repository=` and `commit=` from `upstream/master:plugins/<name>`: that commit is **old**.
- **new** is the head of the plugin repo's default branch on GitHub (`gh api repos/<owner>/<repo>/commits/<branch> --jq .sha`). Unpushed local work does not count.
- old == new: stop, report nothing to bump.

Done when old and new are both full 40-char SHAs.

## 2. Read version

Version is the `version = '...'` line in `build.gradle` at **new**. Treat it as unset when missing or still the template's `1.0-SNAPSHOT`.

## 3. Build changeset

`gh api repos/<owner>/<repo>/compare/<old>...<new>` lists commits and files. Read commit messages and skim diffs until every commit is classified:

- **player-facing**: features, fixes, UI, new or changed settings. Goes in the PR.
- **heads-up**: changed defaults, removed features, anything new sent off the client. Goes in the PR. New outbound data also means the `warning=` line may need updating: flag it to the user.
- **internal**: refactors, tests, docs, build, dev-only tooling, version bump itself. Left out.

## 4. Branch and commit

- Branch from `upstream/master` named `<name>-bump-<n>`, `n` the next number not on origin (first bump has no suffix).
- Set `commit=<new>` in `plugins/<name>`. Touch no other line unless the user approves a `warning=` change.
- Commit message equals the PR title.

## 5. Draft PR

Title: `Update <name> to v<version>`, or `Update <name>` when version unset. No conventional-commit prefix.

Body, written for players in plain words (behaviour, not code):

```markdown
## Changes

- **<Short label>:** <one sentence>.

## Heads up

- <one line per heads-up item>

Generated-by: Claude Code
```

Drop `## Heads up` when empty. After the last bullet comes only the `Generated-by: Claude Code` footer, which the official template's `AGENTS.md` asks for on plugin-hub PRs; if the plugin repo has an `AGENTS.md`, use the footer wording from its `## Submitting` section. No SHAs, class names, config keys, endpoints, or other trailer lines.

Show title and body to the user and wait for approval.

## 6. Open PR

`git push -u origin <branch>`, then `gh pr create --repo runelite/plugin-hub --base master --head <fork-owner>:<branch>` with the approved title and body. Report the PR URL.
