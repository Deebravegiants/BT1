# [M] ALPINE-CVE-2023-48231

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-48231
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2023-11-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-48231
Type: osv

## Affected
- Alpine:v3.19: `vim` — affected >=0 <9.0.2112-r0
- Alpine:v3.20: `vim` — affected >=0 <9.0.2112-r0
- Alpine:v3.21: `vim` — affected >=0 <9.0.2112-r0
- Alpine:v3.22: `vim` — affected >=0 <9.0.2112-r0
- Alpine:v3.23: `vim` — affected >=0 <9.0.2112-r0

## Details
Vim is an open source command line text editor. When closing a window, vim may try to access already freed window structure. Exploitation beyond crashing the application has not been shown to be viable. This issue has been addressed in commit `25aabc2b` which has been included in release version 9.0.2106. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-48231
