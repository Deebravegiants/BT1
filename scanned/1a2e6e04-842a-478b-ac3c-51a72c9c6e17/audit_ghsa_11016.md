# [H] GitHub Copilot CLI Dangerous Shell Expansion Patterns Enable Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-g8r9-g2v8-jv6f
CVE: CVE-2026-29783
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-06
Source: https://github.com/advisories/GHSA-g8r9-g2v8-jv6f
Type: github-advisory

## Affected
- npm: `@github/copilot` — affected >=0 <0.0.423

## Details
## Summary

A security vulnerability has been identified in GitHub Copilot CLI's shell tool that could allow arbitrary code execution through crafted bash parameter expansion patterns. An attacker who can influence the commands executed by the agent (e.g., via prompt injection through repository files, MCP server responses, or user instructions) can exploit bash parameter transformation operators to execute hidden commands, bypassing the safety assessment that classifies commands as "read-only."

## Details

The vulnerability stems from how the CLI's shell safety assessment evaluates commands before execution. The safety layer parses and classifies shell commands as either read-only (safe) or write-capable (requires user approval). However, several bash parameter expansion features can embed executable code within arguments to otherwise read-only commands, causing them to appear safe while actually performing arbitrary operations.

The specific dangerous patterns are:

1. **`${var@P}` — Prompt expansion:** The `@P` parameter transformation operator evaluates its value as a prompt string, which interprets embedded command substitutions. This allows hidden command execution inside what appears to be a simple variable reference.

2. **`${var=value}` / `${var:=value}` — Assignment side-effects:** These forms assign values to variables as a side-effect of expansion. When chained with `@P`, an attacker can progressively build up a command substitution string across multiple expansions.

3. **`${!var}` — Indirect expansion:** Dereferences an arbitrary variable name, which can be combined with other patterns to construct and execute commands dynamically.

4. **Nested `$(cmd)` or `<(cmd)` inside `${...}` expansions:** Command substitution or process substitution embedded within parameter expansion default values (e.g., `${HOME:-$(whoami)}`) executes the nested command.

### Proof of Concept

The following command appears to run a harmless `echo`, but actually executes `touch /tmp/pwned` through chained parameter expansion:

```bash
echo ${a="$"}${b="$a(touch /tmp/pwned)"}${b@P}
```

**How it works:**
- `${a="$"}` assigns the literal `$` character to variable `a`
- `${b="$a(touch /tmp/pwned)"}` expands `$a` to `$`, constructing the string `$(touch /tmp/pwned)` and assigning it to `b`
- `${b@P}` applies prompt expansion to `b`, which evaluates the embedded `$(touch /tmp/pwned)` command substitution

Prior to the fix, the safety assessment would classify `echo` as a read-only command and allow execution without user confirmation — even in modes that normally require approval for write operations.

## Impact

An attacker who can influence command text sent to the shell tool — for example, through:
- Prompt injection via malicious repository content (README files, code comments, issue bodies)
- Compromised or malicious MCP server responses
- Crafted user instructions containing obfuscated commands

— could achieve arbitrary code execution on the user's workstation. This is possible even in permission modes that require user approval for write operations, since the commands can appear to be using only read-only utilities to ultimately trigger write operations.

Successful exploitation could lead to data exfiltration, file modification, or further system compromise.

## Affected Versions

- GitHub Copilot CLI versions prior to 0.0.423

## Remediation and Mitigation

### Fix

The fix adds three layers of defense:

1. **Parse-time detection:** The shell safety assessment analyzes `${...}` expansion nodes within bash commands, detecting dangerous operators (`@P`, `=`, `:=`, `!`) and nested command/process substitutions. Commands containing these patterns are downgraded from read-only to write-capable, ensuring they require user approval.

2. **Unconditional blocking:** Commands with dangerous expansion patterns are unconditionally blocked at the tool execution layer — regardless of permission mode (including `--yolo` / autopilot). This prevents exploitation even when all commands are auto-approved.

3. **System prompt hardening:** The bash shell tool's system prompt now includes explicit instructions for the LLM to refuse executing commands with these patterns, providing a defense-in-depth layer.

### User Actions

1. **Upgrade** GitHub Copilot CLI to **0.0.423** or later.
2. **Exercise caution** when working in untrusted repositories or with untrusted MCP servers.
3. **Review** any shell commands suggested by the agent that contain complex parameter expansion patterns.

## References
- https://github.com/github/copilot-cli/security/advisories/GHSA-g8r9-g2v8-jv6f
- https://nvd.nist.gov/vuln/detail/CVE-2026-29783
- https://github.com/github/copilot-cli
- https://github.com/github/copilot-cli/releases/tag/v0.0.423
