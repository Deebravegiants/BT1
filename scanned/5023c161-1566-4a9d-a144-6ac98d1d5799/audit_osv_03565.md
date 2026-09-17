# [C] ALPINE-CVE-2026-29518

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-29518
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-29518
Type: osv

## Affected
- Alpine:v3.20: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.21: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.4.3-r0

## Details
Rsync versions before 3.4.3 contain a time-of-check to time-of-use (TOCTOU) race condition in daemon file handling that allows attackers to redirect file writes outside intended directories by replacing parent directory components with symbolic links. Attackers with write access to a module path can exploit this race condition to create or overwrite arbitrary files, potentially modifying sensitive system files and achieving privilege escalation when the daemon runs with elevated privileges. This vulnerability can only be triggered if the chroot setting is false.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-29518
