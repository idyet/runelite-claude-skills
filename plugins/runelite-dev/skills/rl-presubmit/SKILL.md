---
name: rl-presubmit
description: Run a pre-submission checklist on a RuneLite plugin (build warnings, LICENSE, icon, README, runelite-plugin.properties, plugin rules & restrictions, and the example-plugin AGENTS.md guidelines) and guide the Plugin Hub PR. Use when the user is preparing to submit, release, or publish a RuneLite plugin.
---

Run a pre-submission checklist for a RuneLite Plugin Hub plugin. Work through each section below in order, reporting findings and fixing issues where possible.

## 1. Compile & surface warnings

Run `./gradlew compileJava` and capture the output. Report:
- Any compilation errors (must fix)
- Any deprecation warnings: identify exactly which API calls are deprecated and suggest modern alternatives
- Any other warnings

## 2. Unused imports

Grep all Java source files for imports and cross-reference against actual usage. Report any unused imports and remove them.

## 3. Unreachable or dead code

Look for any obvious dead code, commented-out code blocks, or TODO/FIXME comments that should be resolved before submission.

## 4. LICENSE check

Check whether a `LICENSE` file exists at the repo root. If absent, inform the user that the Plugin Hub CI will reject the PR with "Missing LICENSE file" and that they must add one. The Plugin Hub recommends the BSD 2-Clause license. If the file is missing, create it now using the BSD 2-Clause template, substituting the current year and the `author` value from `runelite-plugin.properties` as the copyright holder.

## 5. Icon check

Check whether an `icon.png` exists at the repo root. If absent, remind the user that the Plugin Hub will show a generic placeholder and that the icon must be at most 48×72px.

## 6. README check

Check whether a `README.md` exists at the repo root. The Plugin Hub renders the README on the plugin's listing page, so it is strongly recommended (its absence will not fail CI, but the listing will be bare).

- If absent, offer to create a starter `README.md` with a title from `displayName`, a summary from the `description` in `runelite-plugin.properties`, and a "Configuration" section listing each `@ConfigItem` (`name` + `description`) from the config interface.
- If present, verify it actually describes the plugin (not leftover template/placeholder text), matches the current `displayName`/`description`, and documents the config options. Flag any drift between the README and the plugin's actual behavior.

## 7. `runelite-plugin.properties` review

Read the file and verify:
- `displayName` is set and descriptive
- `author` matches the user's GitHub handle
- `build` is set (`build=standard`, or `build=gradle` if the plugin customizes `build.gradle`/adds dependencies). Missing `build` causes the packager to fail the PR with `"build" must be set`.
- `description` is clear and accurately describes what the plugin does
- `version` is set and is a semantic version matching `^\d+\.\d+\.\d+$` (e.g. `1.0.0`; no `-SNAPSHOT`, no two-part `1.9`). If missing, add `version=1.0.0`. If malformed, fix it.
- `version` is the only place the version lives: `build.gradle` must read it from this file (`pluginManifest.getProperty('version')`), not hardcode its own `version = '...'`. If hardcoded, replace it with the manifest-reading block from the `rl-new-plugin` skill.
- If this is an update to an already-published plugin, run `git log --oneline <last-submitted-commit>..HEAD` (the commit in the plugin-hub `plugins/<slug>` file) and confirm `version` was bumped since then, at the right level: PATCH for fixes, MINOR for features/new config, MAJOR for breaking changes (removed/renamed config keys). Flag if unbumped or under-bumped.
- `tags` are relevant and lowercase
- `plugins` points to the correct fully-qualified plugin class

## 8. Rules & restrictions review

Fetch the official template's agent guidelines live (they change, so do not rely on cached knowledge or a local copy). Run exactly this, with no pipe or redirect, and read the full output:
```bash
curl -fsSL https://raw.githubusercontent.com/runelite/example-plugin/master/AGENTS.md
```
If the fetch fails, say so and mark steps 8 and 9 as unverified in the summary.

Read all plugin source files and check them against every category in the `# Plugin Rules & Restrictions` section. Anything listed there is an automatic rejection. Search for the forbidden language features directly rather than relying on a read-through:
```bash
grep -rnE 'java\.lang\.reflect\.(Field|Method|Constructor|Proxy|InvocationHandler|Array)|\.getDeclared(Field|Method|Constructor)s?\(|setAccessible|com\.sun\.jna|System\.(load|loadLibrary)\(|sun\.misc\.Unsafe|org\.lwjgl|ProcessBuilder|Runtime\.getRuntime\(\)\.exec|ClassLoader|defineClass|ObjectInputStream|ObjectOutputStream|implements Serializable' src/main/
```
Only `src/main/` ships; test code may use reflection. `java.lang.reflect.Type` for Gson's `TypeToken` is deliberately not matched, since it is standard and accepted. Judge each hit in context (e.g. `getClass().getClassLoader().getResource(...)` for loading a bundled resource is fine).

RuneLite's Rejected or Rolled Back Features wiki also has its own list of forbidden Java functions, classes and patterns, which AGENTS.md does not repeat. Fetch it with `curl -fsSL 'https://raw.githubusercontent.com/wiki/runelite/runelite/Rejected-or-Rolled-Back-Features.md'`, read its forbidden-code section, then search for the items that can be grepped:
```bash
grep -rnE 'Desktop\.(open|browse|getDesktop)|LinkBrowser\.open|Thread\.(sleep|interrupt)|\.interrupt\(\)|\.menuAction\(|java\.io\.(File|FileInputStream|FileOutputStream|FileReader|FileWriter|RandomAccessFile)\b|new File\(|java\.lang\.Runtime|Runtime\.getRuntime|KeyboardFocusManager|java\.awt\.Robot|new Robot\(|HttpURLConnection|java\.net\.http|new Gson\(|new GsonBuilder\(|new OkHttpClient\(|OkHttpClient\.Builder\(|^package net\.runelite' src/main/
```
`LinkBrowser.browse`, `gson.newBuilder()` and `okHttpClient.newBuilder()` on the injected instances are allowed and not matched. `client.menuAction` has one allowed use (the collection log search toggle quoted on the wiki); anything else is a rejection. The wiki notes older plugins may be grandfathered, but an update to one is reviewed against the current rules. Then check the behaviour rules (boss & combat, PvP, menu, interface, input, data & privacy, content) against what the code actually does, and cite the rule and category for each finding.

Also flag, from Jagex's guidelines:
- Automation of player actions (auto-clicking, auto-alching, prayer flicking helpers)
- Input broadcasting or multi-boxing support
- Revealing information about other players in PvP not visible in the vanilla client (prayers, attack ranges, etc.)
- Anything that reads or writes game data outside of the RuneLite API

## 9. RuneLite Plugin Hub conventions

Check the source against every section of the agent-guidelines half of the fetched file (everything before `# Plugin Rules & Restrictions`) (logging, threading, performance, API usage, HTTP & JSON, file I/O, config, setup & packaging, resources & assets, cleanup). Report each violation with the guideline it breaks. Pay particular attention to:
- `log.info` in per-tick, per-frame, or per-event code
- `Thread.sleep`, blocking IO or OkHttp `execute()` on the client thread, unbounded `Process.waitFor()`
- Hardcoded IDs where `net.runelite.api.gameval` constants exist
- `HttpURLConnection`, `java.net.http`, Apache HttpClient, or `new Gson()` instead of injected `OkHttpClient` / `Gson`
- `build.gradle` declaring dependencies that `runelite-client` already provides (gson, guice, okhttp)
- File IO not going through `Filepath`, or `JFileChooser` instead of `Filepath.Chooser`
- Config group not specific to this plugin; renamed config keys or groups without a migration; a third-party-server toggle that is not opt-in with the required `warning`
- Template leftovers (`com.example`, `Example*` classes, `"example"` config group) or a `META-INF/services/net.runelite.client.plugins.Plugin` file
- `icon.png` that is oversized or not actually a PNG (`file icon.png`)

Also check these common rejection causes:
- Plugin class not extending `Plugin`
- Missing `@PluginDescriptor`
- Config interface not annotated with `@ConfigGroup`
- Overlay not registered/unregistered in `startUp`/`shutDown`
- Client API calls made off the client thread (outside `@Subscribe` handlers or `clientThread.invokeLater`)
- Any dependency on internal RuneLite classes not part of the public API (e.g. core plugin classes)

## 10. Summary

Produce a concise table with two columns, **Ready** and **Needs Attention**, summarising findings from all sections. For anything in Needs Attention, include a one-line description of what to do.

## 11. Submission steps

If Needs Attention is empty: for a first-time submission, read [references/submission.md](references/submission.md) and walk the user through it. For an update to an already-published plugin, point the user to the `rl-bump` skill instead.
