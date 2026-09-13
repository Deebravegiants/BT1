# [M] OpenClaw: Symlink Traversal via IDENTITY.md appendFile in agents.create/update (Incomplete Fix for CVE-2026-32013)

## Summary
Severity: Medium
Advisory: GHSA-7xr2-q9vf-x4r5
CVE: CVE-2026-35632
CWE: CWE-61
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-7xr2-q9vf-x4r5
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0

## Details
### Summary

The patch for CVE-2026-32013 introduced symlink resolution and workspace boundary enforcement for `agents.files.get` and `agents.files.set`. However, two other handlers in the same file (`agents.create` and `agents.update`) still use raw `fs.appendFile` on the `IDENTITY.md` file **without any symlink containment check**. An attacker who can place a symlink in the agent workspace can hijack the `IDENTITY.md` path to append attacker-controlled content to arbitrary files on the system.

### Details

In `src/gateway/server-methods/agents.ts`, the `agents.create` handler constructs the identity path and appends agent metadata without verifying symlinks:

```typescript
// agents.create — line 283-291
const identityPath = path.join(workspaceDir, DEFAULT_IDENTITY_FILENAME);
const lines = [
  "",
  `- Name: ${safeName}`,
  ...(emoji ? [`- Emoji: ${sanitizeIdentityLine(emoji)}`] : []),
  ...(avatar ? [`- Avatar: ${sanitizeIdentityLine(avatar)}`] : []),
  "",
];
await fs.appendFile(identityPath, lines.join("\n"), "utf-8"); // ← NO SYMLINK CHECK
```

The `agents.update` handler has the same issue at line 348-349:

```typescript
// agents.update — line 348-349
const identityPath = path.join(workspace, DEFAULT_IDENTITY_FILENAME);
await fs.appendFile(identityPath, `\n- Avatar: ${sanitizeIdentityLine(avatar)}\n`, "utf-8"); // ← NO SYMLINK CHECK
```

`fs.appendFile` follows symlinks by default. If the `IDENTITY.md` file in the workspace is a symlink pointing to a sensitive file (e.g., `/etc/crontab`, `~/.bashrc`, or `~/.ssh/authorized_keys`), calling `agents.create` will append the agent identity metadata to that file.

The `ensureAgentWorkspace` function (called at line 274 before the append) uses exclusive-create mode (`flag: 'wx'`) for `IDENTITY.md`. If a symlink already exists at that path, the `EEXIST` error is silently caught, and the subsequent `fs.appendFile` follows the symlink.

**Attack flow:**
```
1. Attacker plants symlink: workspace/IDENTITY.md → /etc/crontab
2. ensureAgentWorkspace skips creation (EEXIST from symlink)
3. fs.appendFile follows symlink → writes to /etc/crontab
4. Attacker-controlled content (name, emoji, avatar) injected into crontab → RCE
```

### PoC

**Prerequisites:** Docker and Python 3 installed.

**Step 1: Build and start the test environment.**
```bash
cd llm-enhance/cve-finding/RCE/CVE-2026-32013-identity-appendFile-variant-exp/
docker compose up -d --build
sleep 3
```

**Step 2: Run the exploit.**
```bash
python3 poc_exploit.py
```

This script:
1. Plants a symlink `IDENTITY.md → /etc/target-file.txt` inside the agent workspace
2. Calls the `agents.create` API endpoint via HTTP POST
3. Verifies that the agent identity metadata was appended to `/etc/target-file.txt`

**Step 3: Run the control experiment.**
```bash
python3 control-patched_realpath.py
```

**Step 4: Cleanup.**
```bash
docker compose down
```

### Log of Evidence

**Exploit output:**
```
=== CVE-2026-32013 Variant: Symlink Traversal via IDENTITY.md appendFile ===
[*] Planting symlink: IDENTITY.md -> /etc/target-file.txt
[*] Symlink: lrwxrwxrwx 1 root root 20 /workspaces/evil-agent/IDENTITY.md -> /etc/target-file.txt
[*] Original /etc/target-file.txt: ORIGINAL_SENSITIVE_CONTENT

[*] Calling agents.create with name='evil-agent'...
[*] API response: {'ok': True, 'agentId': 'evil-agent', 'workspace': '/workspaces/evil-agent'}

[*] /etc/target-file.txt after exploit:
    ORIGINAL_SENSITIVE_CONTENT

- Name: evil-agent
- Emoji: 💀
- Avatar: evil.png

[+] SUCCESS! Symlink traversal confirmed.
[+] fs.appendFile followed IDENTITY.md symlink and wrote to /etc/target-file.txt
[+] Attacker-controlled content injected into arbitrary file.
```

**Control output:**
```
=== CONTROL: Patched agents.create blocks symlink traversal ===
[*] Planting symlink: IDENTITY.md -> /etc/target-file.txt
[*] Original /etc/target-file.txt: ORIGINAL_SENSITIVE_CONTENT

[*] Calling PATCHED agents.create with name='safe-agent'...
[*] API response: {'ok': False, 'error': 'symlink_traversal_blocked', 'realPath': '/etc/target-file.txt'}

[*] /etc/target-file.txt after patched call: ORIGINAL_SENSITIVE_CONTENT

[+] CONTROL PASSED: Patched endpoint detected and blocked symlink traversal.
[+] /etc/target-file.txt remains unchanged.
```

### Impact

An attacker who can plant a symlink in the agent workspace directory can use the `agents.create` or `agents.update` gateway API to **append attacker-controlled content to arbitrary files** on the system. If the target file is:

- `/etc/crontab` or user crontab → **Remote Code Execution**
- `~/.bashrc` or `~/.profile` → **Persistent code execution on login**
- `~/.ssh/authorized_keys` → **Unauthorized SSH access**
- Application configuration files → **Service disruption**

The attacker-controlled content includes the agent name (arbitrary string), emoji, and avatar fields, which are only lightly sanitized (whitespace normalization via `sanitizeIdentityLine`).

### Affected products
- **Ecosystem**: npm
- **Package name**: openclaw
- **Affected versions**: <= 2026.2.22
- **Patched versions**: None

### Occurrences

| Permalink | Description |
| :--- | :--- |
| [https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/agents.ts#L283-L291](https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/agents.ts#L283-L291) | `agents.create` handler uses `fs.appendFile` on `IDENTITY.md` without symlink resolution or workspace boundary check. |
| [https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/agents.ts#L348-L349](https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/agents.ts#L348-L349) | `agents.update` handler uses `fs.appendFile` on `IDENTITY.md` without symlink resolution or workspace boundary check. |
| [https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/agents.ts#L274](https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/agents.ts#L274) | `ensureAgentWorkspace` is called before append, but its exclusive-create (`wx`) flag silently skips existing symlinks (EEXIST). |

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7xr2-q9vf-x4r5
- https://nvd.nist.gov/vuln/detail/CVE-2026-35632
- https://github.com/advisories/GHSA-fgvx-58p6-gjwc
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/agents.ts#L274
- https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/agents.ts#L283-L291
- https://github.com/openclaw/openclaw/blob/main/src/gateway/server-methods/agents.ts#L348-L349
- https://www.vulncheck.com/advisories/openclaw-symlink-traversal-via-identity-md-appendfile-in-agents-create-update
