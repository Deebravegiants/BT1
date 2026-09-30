# [C] ALPINE-CVE-2026-53803

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-53803
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-53803
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync before 3.5.0 contains a symlink following vulnerability that allows local attackers to overwrite arbitrary files by placing a symlink at a predictable output path such as --log-file, --write-batch, or daemon-mode log and statistics paths. Attackers can exploit rsync's failure to reject symlinks during ancillary file writes to redirect output to arbitrary filesystem locations, achieving local privilege escalation on installations where rsync runs with elevated privileges such as setuid or privileged daemon configurations.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-53803
