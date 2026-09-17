# [M] ALPINE-CVE-2026-70458

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-70458
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-70458
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync 3.0.0 before 3.5.0 contains an out-of-bounds write vulnerability that allows attackers to corrupt memory by triggering HLINK_BUMP processing on file entries with the FLAG_HLINKED flag set while the hard-link preservation option is inactive. Attackers can exploit the missing F_SUM field in the file_struct layout to access memory past the end of the allocated structure, corrupting adjacent heap or stack data.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-70458
