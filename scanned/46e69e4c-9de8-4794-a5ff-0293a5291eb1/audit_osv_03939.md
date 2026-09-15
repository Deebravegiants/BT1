# [H] ALPINE-CVE-2026-70463

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-70463
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-70463
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=3.1.0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=3.1.0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=3.1.0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=3.1.0 <3.5.0-r0

## Details
rsync 3.1.0 before 3.5.0 contains an authorization bypass in auth users directive parsing. The auth users parser uses comma-only tokenization when splitting the user list, which fails to correctly handle entries of the form @Group Name where the group name contains a space. The space within the group name causes the parser to split the entry at the space boundary, discarding the deny rule associated with the group. An authenticated user whose username or group membership would be denied by an @Group Name auth users entry can connect to a restricted module because the deny rule is silently discarded during parsing.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-70463
