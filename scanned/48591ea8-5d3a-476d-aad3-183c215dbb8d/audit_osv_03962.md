# [M] ALPINE-CVE-2026-7774

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-7774
Ecosystem: Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-7774
Type: osv

## Affected
- Alpine:v3.24: `python3` — affected >=0 <3.14.7-r0

## Details
tarfile.data_filter could be bypassed using crafted link entries, including symlinks with empty or directory-like names, to redirect later archive members outside the intended extraction directory. This allowed a malicious tar archive to cause tarfile.extractall() to write files outside the destination directory, subject to the permissions of the extracting process.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-7774
