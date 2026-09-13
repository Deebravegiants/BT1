# [H] ALPINE-CVE-2025-46334

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-46334
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-46334
Type: osv

## Affected
- Alpine:v3.19: `git` — affected >=0 <2.43.7-r0
- Alpine:v3.20: `git` — affected >=0 <2.45.4-r0
- Alpine:v3.21: `git` — affected >=0 <2.47.3-r0
- Alpine:v3.22: `git` — affected >=0 <2.49.1-r0
- Alpine:v3.23: `git` — affected >=0 <2.50.1-r0
- Alpine:v3.24: `git` — affected >=0 <2.50.1-r0

## Details
Git GUI allows you to use the Git source control management tools via a GUI. A malicious repository can ship versions of sh.exe or typical textconv filter programs such as astextplain. Due to the unfortunate design of Tcl on Windows, the search path when looking for an executable always includes the current directory. The mentioned programs are invoked when the user selects Git Bash or Browse Files from the menu. This vulnerability is fixed in 2.43.7, 2.44.4, 2.45.4, 2.46.4, 2.47.3, 2.48.2, 2.49.1, and 2.50.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-46334
