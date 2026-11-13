# Plugin Hub submission

First-time submission walkthrough for the `rl-presubmit` skill, used once the checklist shows nothing in Needs Attention. Updates to an already-published plugin use the `rl-bump` skill instead.

If the summary shows no items in Needs Attention, guide the user through submitting to the Plugin Hub:

1. Confirm the latest commit is pushed to GitHub and run `git rev-parse HEAD` to get the full 40-character SHA.
2. Instruct the user to fork https://github.com/runelite/plugin-hub on GitHub if they haven't already.
3. In their fork, create the file `plugins/<plugin-slug>` (the slug is the `displayName` lowercased with spaces replaced by hyphens) containing exactly:
   ```
   repository=https://github.com/<github-handle>/<repo-name>.git
   commit=<full 40-char SHA>
   ```
4. Remind the user that the repository must be public and the commit must be the exact SHA they want published, not a branch name.
5. Instruct them to open a pull request from their fork to `runelite/plugin-hub` and fill in the PR description explaining what the plugin does. If Claude drafted the PR, end the description with the `Generated-by: Claude Code` footer that the template's `AGENTS.md` asks for (check its `## Submitting` section for the current wording).
6. Note that CI will run automated checks and a maintainer will review. Common reasons for rejection to watch for: violating Jagex guidelines, depending on internal RuneLite APIs, or duplicating existing Plugin Hub functionality.
