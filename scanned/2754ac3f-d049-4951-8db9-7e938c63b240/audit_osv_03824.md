# [M] ALPINE-CVE-2026-53800

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-53800
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-53800
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync before 3.5.0 contains a symlink race condition vulnerability in the --remove-source-files feature that allows attackers with symlink creation access to cause arbitrary file deletion. Attackers can atomically substitute a symlink for a source file between transfer completion and the unlink() call, causing rsync to delete the symlink target rather than the intended source file.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-53800
