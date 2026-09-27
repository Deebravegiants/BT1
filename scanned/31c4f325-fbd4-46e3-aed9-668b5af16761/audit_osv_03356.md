# [H] ALPINE-CVE-2025-59466

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-59466
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-59466
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.22.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.13.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.13.0-r0

## Details
We have identified a bug in Node.js error handling where "Maximum call stack size exceeded" errors become uncatchable when `async_hooks.createHook()` is enabled. Instead of reaching `process.on('uncaughtException')`, the process terminates, making the crash unrecoverable. Applications that rely on `AsyncLocalStorage` (v22, v20) or `async_hooks.createHook()` (v24, v22, v20) become vulnerable to denial-of-service crashes triggered by deep recursion under specific conditions.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-59466
