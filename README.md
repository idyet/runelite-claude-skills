# runelite-claude-skills

Claude Code skills for building [RuneLite Plugin Hub](https://github.com/runelite/plugin-hub) plugins, from first idea to Hub PR.

Every check fetches its sources live (Jagex's Third Party Client Guidelines, RuneLite's [Rejected or Rolled Back Features](https://github.com/runelite/runelite/wiki/Rejected-or-Rolled-Back-Features), and the [example-plugin](https://github.com/runelite/example-plugin) `AGENTS.md` rules), so verdicts track the current rules rather than a stale copy.

## Install

In Claude Code:

```
/plugin marketplace add idyet/runelite-claude-skills
/plugin install runelite-dev@runelite-dev
```

Skills are namespaced by the plugin, e.g. `/runelite-dev:rl-check-concept`. Claude also picks them up on its own when you talk about building a RuneLite plugin.

To update later: `/plugin marketplace update runelite-dev`, then `/plugin update runelite-dev@runelite-dev`.

## Skills

| Skill | What it does |
|---|---|
| `rl-check-concept` | Vets a plugin idea against Jagex's guidelines, RuneLite's rejected features, and the Plugin Rules & Restrictions. Ends with PASS, NEEDS CHANGES, BLOCK, or INCONCLUSIVE, citing the exact rule. Run it first, before any design or code. |
| `rl-dupe-plugin-check` | Searches all Plugin Hub plugins (names, descriptions, tags) and core RuneLite for duplicates and near-neighbours. Ends with CLEAR, SIMILAR, OVERLAP, DUPLICATE, or INCONCLUSIVE, with repo links. |
| `rl-new-plugin` | Scaffolds a plugin by cloning `runelite/example-plugin` and renaming everything, after both checks above pass. Adds plugin/config/overlay classes, a BSD-2 LICENSE, local build tweaks, and a first commit. |
| `rl-presubmit` | Pre-submission checklist: build warnings, LICENSE, icon, README, `runelite-plugin.properties`, forbidden APIs and patterns, and the `AGENTS.md` guidelines. Then walks you through the Hub PR. |
| `rl-bump` | Updates your plugin's commit in your `plugin-hub` fork and opens the update PR with a player-facing changelog. Manual only: run `/runelite-dev:rl-bump <plugin-name>`. |

Typical flow: `rl-check-concept` → `rl-dupe-plugin-check` → `rl-new-plugin` → build it → `rl-presubmit` → submit → `rl-bump` for later releases.

## Requirements

- `git`, `curl`, and `python3` on your `PATH`
- [GitHub CLI](https://cli.github.com/) (`gh`), authenticated, for `rl-bump` and the author default in `rl-new-plugin`
- A JDK in the range the template's Gradle version supports (JDK 11 to 23 for Gradle 8.10). `rl-new-plugin` finds an installed one if your default JDK is out of range.

Claude will ask permission to run `curl` and `python3` the first time each skill uses them.

## These skills do not guarantee acceptance

The checks catch common rejection reasons. RuneLite maintainers make the final call, and the rules change. Read the cited sources yourself when a verdict is borderline.

## License

BSD 2-Clause. See [LICENSE](LICENSE).
