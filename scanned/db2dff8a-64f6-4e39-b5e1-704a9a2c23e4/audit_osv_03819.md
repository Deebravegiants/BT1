# [H] ALPINE-CVE-2026-53793

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-53793
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-53793
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync before 3.5.0 contains a path confinement bypass vulnerability that allows remote clients to escape the intended inner-module root confinement by constructing paths that resolve outside the chroot boundary when the module root contains a /./ boundary marker. Attackers can exploit improper handling of the /./ notation or forge delta-basis transfers referencing xname paths that cross the /./ boundary to gain unauthorized read or write access to files outside the module's subtree.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-53793
