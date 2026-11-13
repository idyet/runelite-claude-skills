---
name: rl-check-concept
description: Vet a RuneLite plugin concept against Jagex's Third Party Client Guidelines, RuneLite's Rejected or Rolled Back Features, and the Plugin Rules & Restrictions in the official example-plugin AGENTS.md. Use FIRST whenever the user proposes, brainstorms, or asks to build a new RuneLite/OSRS plugin, before requirements, design, or scaffolding.
argument-hint: <concept description>
---

Vet a RuneLite plugin concept against Jagex's Third Party Client Guidelines, RuneLite's Rejected or Rolled Back Features, and RuneLite's Plugin Rules & Restrictions before any code is written. Run this BEFORE scaffolding with the `rl-new-plugin` skill. Work through each step in order and end with a clear verdict.

## 1. Establish the concept

If the concept was not already provided, ask for:
- **Plugin name**: working title
- **What it does**: the player-facing behaviour, in 2-3 sentences
- **Data flow**: what game data it reads, and whether it writes/sends anything, automates any action, or reacts to game state on the player's behalf

## 2. Fetch the source guidelines

Always fetch all three live. They change, so do not rely on cached knowledge. Fetch each raw source with its own plain `curl -fsSL '<url>'` command, URL in single quotes (the `?` in the wiki URL is a glob character in zsh): no pipes, no redirects, no saving to disk, no custom user-agent. Do not use WebFetch: it summarises long pages, and every verdict must cite the exact text.

| Source | Command |
|---|---|
| Jagex Third Party Client Guidelines (OSRS Wiki mirror, wikitext; runescape.com blocks automated fetches) | `curl -fsSL 'https://oldschool.runescape.wiki/w/Update:Third_Party_Client_Guidelines?action=raw'` |
| RuneLite Rejected or Rolled Back Features (GitHub wiki, markdown) | `curl -fsSL 'https://raw.githubusercontent.com/wiki/runelite/runelite/Rejected-or-Rolled-Back-Features.md'` |
| RuneLite Plugin Rules & Restrictions (the `# Plugin Rules & Restrictions` half of the official template's agent guidelines) | `curl -fsSL 'https://raw.githubusercontent.com/runelite/example-plugin/master/AGENTS.md'` |

The OSRS Wiki returns 403 to browser-like user-agents; plain `curl` works.

If any fetch fails, tell the user you could not verify against that source. Do **not** issue a clean PASS in that case; treat the result as INCONCLUSIVE (see step 7).

## 3. Check against Jagex guidelines

Evaluate the concept against the fetched guidelines. Recurring red lines to test against (verify each against the live text, do not rely only on this list):
- **No automation of gameplay**: auto-clicking, auto-alching, prayer flicking, auto-anything, or performing an action the player would otherwise do manually
- **One human input per action**: no input broadcasting, multiboxing, or relaying one input to many clients
- **No hidden information**: must not reveal anything the vanilla client hides, especially anything that confers a PvP advantage (opponent prayers, HP, gear, attack-range overlays, etc.)
- **Official client / API only**: no reading or writing process memory, no modifying the game cache, no interacting with the game outside the RuneLite API
- **Must not facilitate rule-breaking**: real-world trading, botting, account sharing

For each relevant point, classify as **clear / borderline / violation** and cite the specific guideline text.

## 4. Check against Rejected or Rolled Back Features

Search the fetched wiki for anything resembling the concept. For each near-match:
- Note the feature name and the stated reason it was rejected or rolled back.
- Decide whether the new concept shares the same disqualifying property, or differs meaningfully enough to be acceptable.

## 5. Check against Plugin Rules & Restrictions

Walk every category in the fetched `# Plugin Rules & Restrictions` section (boss & combat, PvP, menu, interface, input, data & privacy, content, forbidden language features). For each rule the concept touches:
- Quote the rule and name its category.
- Classify as **clear / borderline / violation**.

Forbidden language features (reflection, JNI/JNA, external processes, dynamic code loading, Java serialization) matter at concept stage too: a concept that can only work by launching another program, loading downloaded code, or reading memory is a violation before any code exists.

Note blanket policies the section states (e.g. new high-end PvM boss plugins are not accepted): a concept in that space is ⛔ even if no single rule matches.

## 6. Duplication (out of scope, deferred)

This checklist covers only whether the concept is *allowed*. Whether an equivalent plugin already exists is a separate question handled by the `rl-dupe-plugin-check` skill, which scans the live Plugin Hub and core RuneLite for duplicates and near-neighbours. Do not attempt a duplication verdict here. If the user has not run it yet, note that the `rl-dupe-plugin-check` skill is the next step (and the `rl-new-plugin` skill runs it automatically as a gate).

## 7. Verdict

End with exactly one of:
- ✅ **PASS**: no guideline conflicts, no overlap with rejected features, no plugin rule hit. Safe to proceed to the `rl-new-plugin` skill.
- ⚠️ **NEEDS CHANGES**: describe precisely what to change to bring it into compliance; with those changes it can pass.
- ⛔ **BLOCK**: violates a guideline or plugin rule, or matches a rejected feature with the same disqualifying property. Explain why and cite the source. Recommend not building it as conceived.
- ❓ **INCONCLUSIVE**: a source could not be fetched/verified. State exactly what is unverified.

Cite the specific guideline text, rejected-feature entry, or plugin rule (with its category) for every ⚠️ and ⛔.

When invoked as a gate by the `rl-new-plugin` skill, only a ✅ proceeds automatically. For ⚠️, ⛔, or ❓, stop and require the user to explicitly confirm before any scaffolding happens.
