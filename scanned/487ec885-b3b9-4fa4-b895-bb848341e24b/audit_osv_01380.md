# [H] ALPINE-CVE-2019-12735

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-12735
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.6 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2019-06-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12735
Type: osv

## Affected
- Alpine:v3.10: `vim` — affected >=0 <8.1.1365-r0
- Alpine:v3.11: `vim` — affected >=0 <8.1.1365-r0
- Alpine:v3.12: `vim` — affected >=0 <8.1.1365-r0
- Alpine:v3.13: `vim` — affected >=0 <8.1.1365-r0
- Alpine:v3.14: `vim` — affected >=0 <8.1.1365-r0
- Alpine:v3.15: `vim` — affected >=0 <8.1.1365-r0
- Alpine:v3.16: `vim` — affected >=0 <8.1.1365-r0
- Alpine:v3.17: `vim` — affected >=0 <8.1.1365-r0
- Alpine:v3.18: `vim` — affected >=0 <8.1.1365-r0
- Alpine:v3.19: `vim` — affected >=0 <8.1.1365-r0
- Alpine:v3.20: `vim` — affected >=0 <8.1.1365-r0
- Alpine:v3.21: `vim` — affected >=0 <8.1.1365-r0
- Alpine:v3.22: `vim` — affected >=0 <8.1.1365-r0
- Alpine:v3.23: `vim` — affected >=0 <8.1.1365-r0
- Alpine:v3.7: `vim` — affected >=0 <8.0.1359-r2
- Alpine:v3.8: `vim` — affected >=0 <8.1.1365
- Alpine:v3.9: `vim` — affected >=0 <8.1.1365-r0

## Details
getchar.c in Vim before 8.1.1365 and Neovim before 0.3.6 allows remote attackers to execute arbitrary OS commands via the :source! command in a modeline, as demonstrated by execute in Vim, and assert_fails or nvim_input in Neovim.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12735
