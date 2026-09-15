# [C] ALPINE-CVE-2026-70460

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-70460
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-70460
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync 2.3.3 before 3.5.0 contains a path traversal vulnerability that allows a malicious sender to escape the module root by exploiting symlinks within the module file tree when using --partial-dir or --backup-dir options. Attackers with write access to place a symlink under the module root, or who can exploit a pre-existing trusted symlink, can direct file writes to locations outside the intended module root, achieving arbitrary file write relative to the module root parent.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-70460
