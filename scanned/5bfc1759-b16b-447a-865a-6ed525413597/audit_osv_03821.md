# [H] ALPINE-CVE-2026-53796

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-53796
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-53796
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync before 3.5.0 contains a time-of-check to time-of-use (TOCTOU) race condition vulnerability in the non-daemon receiver's destination directory handling that allows an attacker who can manipulate destination path parent components to redirect file writes to unintended locations. Attackers can substitute a symlink for a component of the destination path between the path resolution and chdir() call, causing the receiver's working directory to be established outside the intended destination tree so that subsequent relative-path file writes land in unintended filesystem locations.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-53796
