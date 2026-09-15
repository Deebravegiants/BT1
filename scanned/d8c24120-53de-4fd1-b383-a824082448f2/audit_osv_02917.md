# [M] ALPINE-CVE-2023-48706

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-48706
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-11-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-48706
Type: osv

## Affected
- Alpine:v3.19: `vim` — affected >=0 <9.0.2127-r0
- Alpine:v3.20: `vim` — affected >=0 <9.0.2127-r0
- Alpine:v3.21: `vim` — affected >=0 <9.0.2127-r0
- Alpine:v3.22: `vim` — affected >=0 <9.0.2127-r0
- Alpine:v3.23: `vim` — affected >=0 <9.0.2127-r0

## Details
Vim is a UNIX editor that, prior to version 9.0.2121, has a heap-use-after-free vulnerability. When executing a `:s` command for the very first time and using a sub-replace-special atom inside the substitution part, it is possible that the recursive `:s` call causes free-ing of memory which may later then be accessed by the initial `:s` command. The user must intentionally execute the payload and the whole process is a bit tricky to do since it seems to work only reliably for the very first :s command. It may also cause a crash of Vim. Version 9.0.2121 contains a fix for this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-48706
