# [M] ALPINE-CVE-2025-23084

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-23084
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-01-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-23084
Type: osv

## Affected
- Alpine:v3.22: `nodejs` — affected >=0 <22.13.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <22.13.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <22.13.1-r0

## Details
A vulnerability has been identified in Node.js, specifically affecting the handling of drive names in the Windows environment. Certain Node.js functions do not treat drive names as special on Windows. As a result, although Node.js assumes a relative path, it actually refers to the root directory.

On Windows, a path that does not start with the file separator is treated as relative to the current directory. 

This vulnerability affects Windows users of `path.join` API.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-23084
