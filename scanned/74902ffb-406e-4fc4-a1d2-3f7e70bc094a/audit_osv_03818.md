# [M] ALPINE-CVE-2026-53792

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-53792
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-53792
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync before 3.5.0 contains an out-of-bounds read vulnerability in the sender-side block matching logic that allows a malicious receiver to trigger memory access before the start of an allocated buffer by sending a crafted checksum block with a length of zero. Attackers can send a specially crafted checksum set containing a zero-length block to cause a negative offset calculation during delta computation, resulting in an out-of-bounds read of file data buffer memory on the sender side.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-53792
