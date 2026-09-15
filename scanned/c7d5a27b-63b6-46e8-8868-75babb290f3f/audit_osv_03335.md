# [M] ALPINE-CVE-2025-55132

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-55132
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-55132
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.22.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.13.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.13.0-r0

## Details
A flaw in Node.js's permission model allows a file's access and modification timestamps to be changed via `futimes()` even when the process has only read permissions. Unlike `utimes()`, `futimes()` does not apply the expected write-permission checks, which means file metadata can be modified in read-only directories. This behavior could be used to alter timestamps in ways that obscure activity, reducing the reliability of logs. This vulnerability affects users of the permission model on Node.js v20,  v22,  v24, and v25.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-55132
