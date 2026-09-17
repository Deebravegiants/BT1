# [M] ALPINE-CVE-2024-8088

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-8088
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:N/AU:N/R:U/V:X/RE:L/U:X)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-8088
Type: osv

## Affected
- Alpine:v3.17: `python3` — affected >=0 <3.10.14-r2
- Alpine:v3.18: `python3` — affected >=0 <3.11.8-r1
- Alpine:v3.19: `python3` — affected >=0 <3.11.9-r1
- Alpine:v3.20: `python3` — affected >=0 <3.12.3-r2
- Alpine:v3.21: `python3` — affected >=0 <3.12.5-r1
- Alpine:v3.22: `python3` — affected >=0 <3.12.5-r1
- Alpine:v3.23: `python3` — affected >=0 <3.12.5-r1
- Alpine:v3.24: `python3` — affected >=0 <3.12.5-r1

## Details
There is a HIGH severity vulnerability affecting the CPython "zipfile"
module affecting "zipfile.Path". Note that the more common API "zipfile.ZipFile" class is unaffected.





When iterating over names of entries in a zip archive (for example, methods
of "zipfile.Path" like "namelist()", "iterdir()", etc)
the process can be put into an infinite loop with a maliciously crafted
zip archive. This defect applies when reading only metadata or extracting
the contents of the zip archive. Programs that are not handling
user-controlled zip archives are not affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-8088
