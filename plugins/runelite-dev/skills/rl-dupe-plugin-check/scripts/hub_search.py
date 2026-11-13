#!/usr/bin/env python3
"""Search the live RuneLite Plugin Hub manifest and core RuneLite plugins.

Usage:
  hub_search.py match KEYWORD [KEYWORD ...]   Hub plugins + core plugin folders matching any keyword
  hub_search.py repo INTERNAL_NAME [...]      repository= line from plugin-hub for each plugin

Stdlib only, nothing written to disk, so it runs the same on macOS, Linux and Windows.
Exits non-zero with a message on any fetch failure: the caller must then report INCONCLUSIVE.
"""
import json
import re
import sys
import urllib.error
import urllib.request

BOOTSTRAP = "https://static.runelite.net/bootstrap.json"
MANIFEST = "https://repo.runelite.net/plugins/manifest/{ver}_full.js"
CORE_PLUGINS = "https://api.github.com/repos/runelite/runelite/contents/runelite-client/src/main/java/net/runelite/client/plugins"
HUB_ENTRY = "https://raw.githubusercontent.com/runelite/plugin-hub/master/plugins/{name}"


def fetch(url):
	req = urllib.request.Request(url, headers={"User-Agent": "runelite-dev-hub-search"})
	with urllib.request.urlopen(req, timeout=30) as resp:
		return resp.read()


def hub_plugins():
	ver = json.loads(fetch(BOOTSTRAP))["version"]
	blob = fetch(MANIFEST.format(ver=ver))
	# Signed blob: 4-byte length + RSA signature, then the JSON, which always starts at {"display":
	start = blob.find(b'{"display":')
	if start < 0:
		raise ValueError("manifest format changed: no {\"display\": marker")
	return ver, json.loads(blob[start:])["display"]


def core_plugins():
	return sorted(e["name"] for e in json.loads(fetch(CORE_PLUGINS)) if e["type"] == "dir")


def match(keywords):
	pat = re.compile("|".join(re.escape(k) for k in keywords), re.I)
	ver, plugins = hub_plugins()
	hits = []
	for p in plugins:
		tags = p.get("tags") or []
		hay = " ".join([p.get("internalName", ""), p.get("displayName", ""), p.get("description", ""), " ".join(tags)])
		if pat.search(hay):
			hits.append(p)
	print(f"# Plugin Hub (client {ver}): {len(hits)} of {len(plugins)} plugins match {keywords}")
	for p in hits:
		print(f"- {p['internalName']} | {p['displayName']} | tags={','.join(p.get('tags') or [])}")
		print(f"    {(p.get('description') or '')[:160]}")
	core = core_plugins()
	core_hits = [c for c in core if pat.search(c)]
	print(f"\n# Core RuneLite: {len(core_hits)} of {len(core)} plugin folders match")
	for c in core_hits:
		print(f"- {c}")
	print("\n# All core plugin folders (scan for matches the keywords missed)")
	print(", ".join(core))


def repo(names):
	failed = []
	for name in names:
		try:
			text = fetch(HUB_ENTRY.format(name=name)).decode()
		except urllib.error.HTTPError as e:
			# One bad name (e.g. a core plugin, which has no hub entry) must not hide the rest
			print(f"{name}: <no plugin-hub entry: HTTP {e.code}>")
			failed.append(name)
			continue
		line = next((l for l in text.splitlines() if l.startswith("repository=")), "repository=<missing>")
		print(f"{name}: {line.split('=', 1)[1]}")
	if failed:
		raise LookupError(f"no plugin-hub entry for {failed}")


def main(argv):
	if len(argv) < 3 or argv[1] not in ("match", "repo"):
		print(__doc__.strip(), file=sys.stderr)
		return 2
	try:
		(match if argv[1] == "match" else repo)(argv[2:])
	except Exception as e:
		print(f"FETCH FAILED: {type(e).__name__}: {e}", file=sys.stderr)
		return 1
	return 0


if __name__ == "__main__":
	sys.exit(main(sys.argv))
