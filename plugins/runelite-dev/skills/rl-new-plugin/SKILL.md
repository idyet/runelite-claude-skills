---
name: rl-new-plugin
description: Scaffold a new RuneLite Plugin Hub plugin by cloning the official runelite/example-plugin template and renaming it (Gradle project, plugin/config/overlay classes, test launcher, agent guidelines, git init). Use when the user wants to start or create a new RuneLite plugin project. Gates on rl-check-concept and rl-dupe-plugin-check first.
argument-hint: <plugin name>
---

Scaffold a new RuneLite Plugin Hub plugin from the official `runelite/example-plugin` template. Follow each step in order.

## 1. Gather plugin details

Ask the user for the following before doing anything else (collect all in one question block):
- **Plugin name**: display name shown in the RuneLite plugin panel (e.g. `Slayer Cape Reminder`)
- **Description**: one sentence describing what the plugin does
- **Tags**: comma-separated keywords (lowercase)
- **GitHub handle**: used as the `author` field in `runelite-plugin.properties` (default: the output of `gh api user --jq .login` if `gh` is authenticated; ask only if that fails)
- **Needs an overlay?**: yes or no
- **Needs a config?**: yes or no

Derive the following from the plugin name:
- **Package name**: lowercase, no spaces or hyphens (e.g. `slayercapereminder`)
- **Class prefix**: PascalCase with no spaces (e.g. `SlayerCapeReminder`)
- **Directory name**: lowercase hyphenated (e.g. `slayer-cape-reminder`). Also used as the config group, which must be specific to this plugin.
- **Repo root**: `<current working directory>/<directory-name>/`. State the full path and let the user redirect it before creating files.

## 2. Vet the concept against compliance guidelines (gate)

Before creating any files, run the `rl-check-concept` skill checklist against the gathered name and description. It fetches its sources live (Jagex guidelines, RuneLite's rejected features, and the template's Plugin Rules & Restrictions); follow it as written rather than summarising it here.

Only a ✅ PASS proceeds automatically. If the verdict is ⚠️ NEEDS CHANGES, ⛔ BLOCK, or ❓ INCONCLUSIVE, stop and require the user to explicitly confirm (or adjust the concept) before continuing to scaffolding.

## 2b. Check for existing/similar plugins (gate)

After the concept passes compliance, run the `rl-dupe-plugin-check` skill checklist against the gathered name and description to make sure the Plugin Hub (or core RuneLite) does not already cover this ground. Duplication of an existing plugin is a common Hub rejection reason.

Only ✅ CLEAR and 🟡 SIMILAR proceed automatically (SIMILAR after confirming the differentiation stands). For 🟠 OVERLAP, ⛔ DUPLICATE, or ❓ INCONCLUSIVE, stop and require the user to explicitly confirm (or adjust the concept) before continuing to scaffolding.

## 3. Clone the template

The repo root must not exist yet. Run:
```bash
git clone --depth 1 https://github.com/runelite/example-plugin.git <repo-root>
rm -rf <repo-root>/.git
```
If the clone fails, stop and report it. Do not hand-write the project instead: the template is the source of truth for `build.gradle`, the Gradle wrapper, `logback-test.xml`, `CLAUDE.md`, and `AGENTS.md`.

Read `<repo-root>/AGENTS.md` now. Its guidelines apply to every file you write from here on.

## 4. Rename everything from the template

AGENTS.md requires no `com.example`, `ExamplePlugin`, `ExampleConfig`, or `example` config group to remain. From the repo root:
- Move `src/main/java/com/example/` to `src/main/java/com/<package-name>/` and `src/test/java/com/example/` to `src/test/java/com/<package-name>/`.
- Rename `ExamplePlugin.java`, `ExampleConfig.java`, `ExamplePluginTest.java` to `<class-prefix>Plugin.java`, `<class-prefix>Config.java`, `<class-prefix>PluginTest.java`, and update the `package` lines and class references inside them.
- `build.gradle`: `group = 'com.<package-name>'` and `pluginMainClass = 'com.<package-name>.<class-prefix>PluginTest'`.
- `settings.gradle`: `rootProject.name = '<directory-name>'`.
- `src/test/resources/logback-test.xml`: `<logger name="com.<package-name>" level="DEBUG" />`.
- `README.md`: replace with `# <Plugin Name>` and the description.

## 5. Apply plugin specifics

Read [references/project-files.md](references/project-files.md) and apply each section:
- **`runelite-plugin.properties`**: overwrite with the gathered details.
- **`build.gradle` additions**: patch them into the template file. Change nothing else in it.
- **`.gitignore` additions**: append to the template's `.gitignore`.
- **`LICENSE`**: create it. The template ships without one, and the Plugin Hub CI rejects PRs with "Missing LICENSE file".
- **`gradle.properties`**: only if the default JDK is outside the range the wrapper's Gradle version supports.
- **Plugin class**: replace the template's greeter demo with the minimal class described.
- **Config interface**: if no config was requested, delete `<class-prefix>Config.java` and its `@Provides` method. Otherwise replace its demo item with the placeholder described.
- **Overlay class**: create it only if requested.

## 6. Check for template leftovers

Run from the repo root:
```bash
grep -rniI 'example' --exclude-dir=.gradle --exclude-dir=build --exclude-dir=gradle --exclude=gradlew --exclude=gradlew.bat --exclude=AGENTS.md --exclude=CLAUDE.md .
```
It must print nothing. Fix every hit before continuing. (`AGENTS.md` and `CLAUDE.md` are excluded because they mention the template by name on purpose.)

## 7. Compile to verify

Run `./gradlew compileJava` and confirm a clean build. Fix any errors before proceeding.

## 8. Initialise git

Run from the repo root:
```
git init
git add .
git status --short
```
Confirm the staged list holds only source and project files: no `build/`, `.gradle/`, `gradle.properties`, or `.class` files. Then:
```
git commit -m "feat: initial <Plugin Name> plugin scaffold"
```

Before committing, run `git config user.name` and `git config user.email` from the repo root and show the user the identity the commit will use. If either is unset, stop and ask them to configure it. Note that this email becomes public once the repo is pushed.

## 9. Summary

Report:
- Repo root path
- Files created
- Whether the build compiled cleanly
- Next steps: implement plugin logic following `AGENTS.md`, then run the `rl-presubmit` skill before pushing to GitHub
