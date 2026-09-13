# [H] ALPINE-CVE-2022-1621

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-1621
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-05-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-1621
Type: osv

## Affected
- Alpine:v3.16: `vim` — affected >=0 <8.2.4969-r0
- Alpine:v3.17: `vim` — affected >=0 <8.2.4969-r0
- Alpine:v3.18: `vim` — affected >=0 <8.2.4969-r0
- Alpine:v3.19: `vim` — affected >=0 <8.2.4969-r0
- Alpine:v3.20: `vim` — affected >=0 <8.2.4969-r0
- Alpine:v3.21: `vim` — affected >=0 <8.2.4969-r0
- Alpine:v3.22: `vim` — affected >=0 <8.2.4969-r0
- Alpine:v3.23: `vim` — affected >=0 <8.2.4969-r0

## Details
Heap buffer overflow in vim_strncpy find_word in GitHub repository vim/vim prior to 8.2.4919. This vulnerability is capable of crashing software, Bypass Protection Mechanism, Modify Memory, and possible remote execution

## References
- https://security.alpinelinux.org/vuln/CVE-2022-1621
