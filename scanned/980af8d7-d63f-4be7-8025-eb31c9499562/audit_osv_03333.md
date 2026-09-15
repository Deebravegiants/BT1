# [C] ALPINE-CVE-2025-55130

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-55130
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-55130
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.22.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.22.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.13.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.13.0-r0

## Details
A flaw in Node.js’s Permissions model allows attackers to bypass `--allow-fs-read` and `--allow-fs-write` restrictions using crafted relative symlink paths. By chaining directories and symlinks, a script granted access only to the current directory can escape the allowed path and read sensitive files. This breaks the expected isolation guarantees and enables arbitrary file read/write, leading to potential system compromise.
This vulnerability affects users of the permission model on Node.js v20,  v22,  v24, and v25.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-55130
