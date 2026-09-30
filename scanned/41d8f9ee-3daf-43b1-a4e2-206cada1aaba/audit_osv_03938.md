# [M] ALPINE-CVE-2026-70462

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-70462
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-70462
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync 3.1.0 before 3.5.0 contains a signed integer overflow vulnerability in the I/O timeout implementation that allows attackers to permanently disable connection timeouts by injecting MSG_IO_TIMEOUT messages carrying non-positive (zero or negative) values. Attackers can craft malicious MSG_IO_TIMEOUT messages that cause the timeout variable to wrap to a non-positive value, preventing the timeout check from firing and enabling idle or stalled connections to hold daemon slots indefinitely, leading to resource exhaustion.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-70462
