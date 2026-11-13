# Plugin specifics

Changes the `rl-new-plugin` skill applies on top of the cloned `runelite/example-plugin` template. Placeholders (`<package-name>`, `<class-prefix>`, `<directory-name>`, etc.) come from its step 1.

## Project files

### `runelite-plugin.properties`
Overwrite the template's file with:
```
displayName=<Plugin Name>
author=<github-handle>
build=standard
description=<description>
version=1.0.0
tags=<tags>
plugins=com.<package-name>.<class-prefix>Plugin
```
`build=standard` is required: the plugin-hub packager fails with `"build" must be set` otherwise. Use `build=gradle` only if you add dependencies or customize `build.gradle`.

`version` is required and must be a semantic version `MAJOR.MINOR.PATCH` (plain numbers, no `-SNAPSHOT` or other suffix). Start every new plugin at `1.0.0`. This file is the single source of truth: `build.gradle` reads it, so never set a version anywhere else. Bump rules for later releases:
- **PATCH**: bug fixes only, no behavior or config changes
- **MINOR**: new features or new config options, backward compatible
- **MAJOR**: breaking changes (removed/renamed config keys, changed default behavior users rely on)

### `build.gradle` additions
Patch these three into the template's `build.gradle`. Leave every other line as the template has it: AGENTS.md requires the file to match the template's structure. With `build=standard` the Plugin Hub replaces this file entirely, so these only affect local builds.

1. Directly below the `group = ...` line, read the version from `runelite-plugin.properties` so the two can never drift:
   ```groovy
   // The Plugin Hub reads the version from runelite-plugin.properties (and with
   // build=standard it replaces this file entirely), so that is the single source of truth.
   // Reading it here keeps the local jar name in step instead of letting the two drift.
   def pluginManifest = new Properties()
   file('runelite-plugin.properties').withInputStream { pluginManifest.load(it) }
   version = pluginManifest.getProperty('version')
   ```
2. Inside the existing `tasks.withType(JavaCompile).configureEach { ... }` block, add a line so deprecated API usage is a build error:
   ```groovy
   options.compilerArgs << '-Xlint:deprecation' << '-Werror'
   ```
3. Inside the existing `run` task, directly below `jvmArgs "-ea"`, add the macOS-only flag. `com.apple.eawt` doesn't exist on Windows/Linux JDKs, where the flag prints a JVM startup warning on every launch. Since `jvmArgs()` appends, add it conditionally:
   ```groovy
   // macOS-only: com.apple.eawt doesn't exist on Windows/Linux JDKs, where the flag would print a
   // JVM startup warning on every launch. jvmArgs() appends, so this adds the flag only on mac.
   if (System.getProperty('os.name').toLowerCase().startsWith('mac')) {
   	jvmArgs '--add-opens=java.desktop/com.apple.eawt=ALL-UNNAMED'
   }
   ```

### `.gitignore` additions
Append to the template's `.gitignore`, skipping any line already present:
```
gradle.properties
*.iml
out/
.DS_Store
```

### `LICENSE`
BSD 2-Clause, the license the Plugin Hub recommends (AGENTS.md requires a permissive one). Create it at the repo root with the current year and the `author` from `runelite-plugin.properties`:
```
BSD 2-Clause License

Copyright (c) <year>, <github-handle>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

### `gradle.properties` (only if needed)
The JDK that runs Gradle must be new enough for the plugin (11+) and old enough for the wrapper's Gradle version. Gradle 8.10, which the template pins today, runs on JDK 11 to 23; on a newer JDK the build fails with `Unsupported class file major version`. If `distributionUrl` in `gradle/wrapper/gradle-wrapper.properties` names a different Gradle version, check its range at https://docs.gradle.org/current/userguide/compatibility.html.

Run `java -version`. If the default JDK is in range, skip this file. Otherwise look for an installed JDK in range (`/usr/libexec/java_home -V` on macOS, `update-alternatives --list java` on Linux), preferring the newest one; ask the user only if none is found. Then create:
```
org.gradle.java.home=<path to in-range JDK>
```
Note: this file is gitignored as it contains a machine-specific path.

## Java source files

### Plugin class: `src/main/java/com/<package-name>/<class-prefix>Plugin.java`

Replace the template's greeter demo with a minimal but complete plugin class:
- `@Slf4j` (Lombok)
- `@PluginDescriptor(name, description, tags)`
- Extends `Plugin`
- `@Inject Client client`
- If overlay requested: `@Inject OverlayManager overlayManager`, `@Inject <class-prefix>Overlay overlay`
- If config requested: `@Inject <class-prefix>Config config`, plus the `@Provides` method kept from the template
- `startUp()`: add overlay if applicable
- `shutDown()`: remove overlay if applicable
- No `onGameStateChanged` greeter or other demo handlers
- Follow RuneLite code style: tabs, Allman-style braces, no wildcard imports

### Config interface (if requested): `src/main/java/com/<package-name>/<class-prefix>Config.java`
- `@ConfigGroup("<directory-name>")`: specific to this plugin, never the template's `"example"`
- Extends `Config`
- Replace the template's `greeting` item with one placeholder `@ConfigItem` as an example

### Overlay class (if requested): `src/main/java/com/<package-name>/<class-prefix>Overlay.java`
- Extends `OverlayPanel`
- `@Inject` constructor taking plugin and config (if applicable)
- `setPosition(OverlayPosition.TOP_LEFT)` in constructor
- `render(Graphics2D)` returning `null` as a stub
