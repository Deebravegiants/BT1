# [H] ALPINE-CVE-2026-53802

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-53802
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-53802
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync before 3.5.0 contains an arbitrary file read vulnerability that allows attackers to read files accessible to the rsync daemon process by exploiting symlink following in input configuration file handling including --files-from, --password-file, and filter merge files. Attackers can place a symlink at a predictable --files-from or --password-file path, or supply a --files-from path that escapes the daemon module root, to read arbitrary files accessible to the rsync process.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-53802
