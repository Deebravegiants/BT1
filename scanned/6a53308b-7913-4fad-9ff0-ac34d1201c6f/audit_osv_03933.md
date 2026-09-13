# [M] ALPINE-CVE-2026-70456

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-70456
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-70456
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync 3.0.1 before 3.5.0 contains an out-of-bounds write vulnerability in the read_args() function that allows a malicious sender to corrupt adjacent heap memory by sending a crafted argument list. When the argument count causes the argv allocation to be exactly full, the trailing NULL terminator is written one slot beyond the allocation boundary, corrupting adjacent heap memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-70456
