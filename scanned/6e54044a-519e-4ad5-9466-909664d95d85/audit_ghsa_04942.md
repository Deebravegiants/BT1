# [H] githubtoplanguages: Command Injection via Issue Title in Discord Notification Workflow

## Summary
Severity: High
Advisory: GHSA-c3xh-98xp-6qhf
CWE: CWE-78
Ecosystem: GitHub Actions
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-c3xh-98xp-6qhf
Type: github-advisory

## Affected
- GitHub Actions: `gouef/githubtoplanguages` — affected >=0 <1.1.4

## Details
### Summary

A GitHub Actions workflow is vulnerable to command injection through the issue title.

The workflow is triggered when an issue is opened or closed, and it directly inserts `github.event.issue.title` into a Bash variable assignment. If an issue title contains command substitution syntax, Bash evaluates it during the workflow run.


### Details

The vulnerable workflow is:

`.github/workflows/discord-issue.yml`

The issue title is directly interpolated into a Bash script:

```bash
ISSUE_TITLE="${{ github.event.issue.title || github.event.pull_request.title }}"
```

Because GitHub Actions expressions are expanded before Bash executes the script, an attacker-controlled issue title containing command substitution syntax can be evaluated by the shell.

In the original workflow, the resulting value is then included in a Discord notification payload:

```bash
curl -H "Content-Type: application/json" \
  -X POST \
  -d "{\"username\": \"GitHub Bot\", \"content\": \"${STATUS} created by **${AUTHOR}**: **${ISSUE_TITLE}**\n🔗 ${ISSUE_URL}\"}" \
  "$DISCORD_WEBHOOK"
```

### PoC

For safety, I reproduced this only in my fork. I did not trigger the original repository’s Discord webhook.

I kept the vulnerable Bash assignment unchanged and replaced the Discord webhook request with `echo` statements to observe the result safely.

Test issue title:

```text
title: $(whoami)
```

Observed workflow log:

```text
ISSUE_TITLE=title: runner
```

This confirms that `$(whoami)` was executed on the GitHub Actions runner before the value would be sent to Discord.

### Impact

Any user who can open an issue may be able to execute shell commands on the GitHub Actions runner.

In practice, this means an attacker could create an issue with a crafted title, cause the workflow to execute a shell command, and have the command output included in the Discord notification content. This can be used to manipulate Discord notifications, spoof trusted GitHub bot messages, or repeatedly trigger unwanted notifications.

More importantly, the command runs in a workflow environment where a Discord webhook secret is configured. Depending on repository settings and workflow permissions, this may put workflow secrets or other environment data at risk.

### Suggested Fix

Do not insert issue titles directly into Bash scripts.

Pass the title through an environment variable instead:

```yaml
env:
  ISSUE_TITLE: ${{ github.event.issue.title }}
run: |
  issue_title="$ISSUE_TITLE"
```

Also avoid `eval`, unquoted variable expansion, or shell execution patterns involving user-controlled issue content.

## References
- https://github.com/gouef/githubtoplanguages/security/advisories/GHSA-c3xh-98xp-6qhf
- https://github.com/gouef/githubtoplanguages/commit/157840482e592bd4f8e0617539e73cdbef26f1ac
- https://github.com/gouef/githubtoplanguages
