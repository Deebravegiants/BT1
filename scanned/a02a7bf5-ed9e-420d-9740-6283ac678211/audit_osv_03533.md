# [M] ALPINE-CVE-2026-27171

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-27171
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-27171
Type: osv

## Affected
- Alpine:v3.20: `zlib` — affected >=1.2.12 <1.3.2-r0
- Alpine:v3.21: `zlib` — affected >=1.2.12 <1.3.2-r0
- Alpine:v3.22: `zlib` — affected >=1.2.12 <1.3.2-r0
- Alpine:v3.23: `zlib` — affected >=1.2.12 <1.3.2-r0
- Alpine:v3.24: `zlib` — affected >=1.2.12 <1.3.2-r0

## Details
zlib before 1.3.2 allows CPU consumption via crc32_combine64 and crc32_combine_gen64 because x2nmodp can do right shifts within a loop that has no termination condition.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-27171
