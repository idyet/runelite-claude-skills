---
name: rl-dupe-plugin-check
description: Search the live RuneLite Plugin Hub manifest and core RuneLite for plugins that duplicate or resemble a proposed concept. Use after rl-check-concept passes, or when the user asks whether a RuneLite plugin like X already exists.
argument-hint: <concept description>
---

Check the RuneLite Plugin Hub (and core RuneLite) for existing plugins that duplicate or resemble a proposed plugin concept. This is a DIFFERENT question from the `rl-check-concept` skill (which asks "is this allowed?"). Here we ask "does something like this already exist?", surfacing near-neighbours, not just exact duplicates. Run this before scaffolding with the `rl-new-plugin` skill, or any time you want to scan prior art. Work through each step in order and end with a clear verdict.

## 1. Establish the concept

If not already provided, ask for:
- **Plugin name**: working title
- **What it does**: player-facing behaviour, in 2-3 sentences
- **Core function**: the one job it exists to do (e.g. "notify when Slayer cape can be equipped", "overlay drop-rate on NPCs")

Then derive a **keyword set** for matching. Include the obvious terms AND synonyms/related jargon, because plugins are often named creatively rather than descriptively:
- Direct terms from the name and function (e.g. `slayer`, `cape`, `reminder`)
- OSRS synonyms and adjacent concepts (e.g. for "cape reminder": `equip`, `notify`, `alert`, `skillcape`, `milestone`)
- The activity/skill/boss/item domain (e.g. `slayer`, `combat`, `pvm`)

The manifest is searched across tags and descriptions (not just names), so a broad, synonym-rich keyword set is what lets tag matches catch creatively-named plugins.

## 2. Search the Plugin Hub and core RuneLite

The list changes constantly. Always search live; never rely on cached knowledge.

RuneLite serves a signed manifest of **every** Hub plugin (`internalName`, `displayName`, `description`, `tags`) in one ~1 MB file with a binary signature prefix. Do NOT fetch it with WebFetch, which mangles or truncates it. Use the bundled script, which downloads it, strips the signature, and matches in memory. Run it as a single command (no pipes, variables, or heredocs), with the script path built from the base directory this skill was loaded from:

```bash
python3 <skill-base-dir>/scripts/hub_search.py match slayer cape skillcape milestone
```

Pass the step 1 keyword set as separate arguments. The script matches each keyword (case-insensitive, substring) against every plugin's `internalName`, `displayName`, `description`, AND `tags`. Matching on tags and descriptions, not just names, is what catches creatively-named plugins: e.g. a "MaxCape" plugin surfaces on the `slayer`/`cape` tags even though its name says neither.

Output has three sections:
- **Plugin Hub**: each match as `internalName | displayName | tags`, with the description below it
- **Core RuneLite**: core plugin folders whose names match a keyword
- **All core plugin folders**: the full list, so you can spot a core plugin the keywords missed (e.g. `xpglobes` for an XP-tracking idea)

If the script exits non-zero (it prints `FETCH FAILED: ...`), you cannot verify against the Hub; report ❓ INCONCLUSIVE (step 6). Do not issue a clean CLEAR.

Expect false positives from broad keywords. That's fine: they get judged next. If the Hub match list is very large (dozens), rerun with keywords tightened toward the concept's core function rather than the domain, and say you did.

## 3. Judge Hub overlap

The match output already gives `displayName` + `description` + `tags`, so judge overlap directly, with no per-plugin secondary fetch needed. Classify each match as:
- **duplicate**: does essentially the same core job
- **overlapping**: covers part of the concept, or the same job with a different scope/trigger
- **adjacent**: same domain, different job (worth citing so the user knows the neighbourhood)

## 4. Check core RuneLite

Some concepts are already bundled in the base client, which is an automatic Hub rejection. From the core sections of the step 2 output, flag any core plugin that already delivers the concept's core function. To confirm what a core plugin covers, read its config interface (e.g. `https://raw.githubusercontent.com/runelite/runelite/master/runelite-client/src/main/java/net/runelite/client/plugins/slayer/SlayerConfig.java`) with a plain `curl -fsSL <url>`.

## 5. Resolve repos for cited plugins

For every Hub plugin you will cite as SIMILAR, OVERLAP, or DUPLICATE, get its repo URL in one call:

```bash
python3 <skill-base-dir>/scripts/hub_search.py repo <internalName> [<internalName> ...]
```

Only for the few cited plugins, not the whole match list. Core plugins have no Hub entry; link them as `https://github.com/runelite/runelite/tree/master/runelite-client/src/main/java/net/runelite/client/plugins/<folder>`.

## 6. Verdict

End with exactly one of:
- ✅ **CLEAR**: no duplicate and no meaningful overlap found on the Hub or in core. Safe to proceed.
- 🟡 **SIMILAR**: related plugins exist but the concept is genuinely differentiated. List each similar plugin, what it does, and the specific way the concept differs. Proceeding is reasonable; the difference is the plugin's reason to exist.
- 🟠 **OVERLAP**: an existing plugin largely covers this, but there is a real unaddressed gap. Name the plugin(s), describe the gap, and recommend scoping the concept down to that gap (or contributing the gap upstream).
- ⛔ **DUPLICATE**: an existing Hub or core plugin already does essentially this. Name it, link its repo, and recommend contributing to it rather than building a new one. Cite what makes it a duplicate.
- ❓ **INCONCLUSIVE**: the plugin list could not be fetched/verified. State exactly what is unverified.

For every SIMILAR / OVERLAP / DUPLICATE candidate cited, include its plugin name and repository URL so the user can inspect it directly.

When invoked as a gate by the `rl-new-plugin` skill, only ✅ CLEAR and 🟡 SIMILAR proceed automatically (SIMILAR after briefly confirming the differentiation stands). For 🟠 OVERLAP, ⛔ DUPLICATE, or ❓ INCONCLUSIVE, stop and require the user to explicitly confirm or adjust before any scaffolding happens.
