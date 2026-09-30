# [M] ALPINE-CVE-2026-70461

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-70461
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-70461
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=3.2.5 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=3.2.5 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=3.2.5 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=3.2.5 <3.5.0-r0

## Details
rsync 3.2.5 before 3.5.0 contains a heap out-of-bounds write vulnerability that allows remote unauthenticated attackers to write one attacker-controlled byte past the end of a heap allocation by supplying a crafted files-from entry. Attackers can trigger the vulnerability against a read-only rsync daemon module by providing a files-from entry containing both an interior and trailing backslash, causing the add_implied_include() function to under-count the trailing backslash when sizing the destination buffer.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-70461
