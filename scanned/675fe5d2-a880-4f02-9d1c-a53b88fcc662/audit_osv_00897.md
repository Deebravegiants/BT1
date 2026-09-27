# [M] ALPINE-CVE-2018-1071

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-1071
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1071
Type: osv

## Affected
- Alpine:v3.10: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.11: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.12: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.13: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.14: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.15: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.16: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.17: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.18: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.19: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.20: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.21: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.22: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.23: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.24: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.4: `zsh` — affected >=0 <5.2-r2
- Alpine:v3.5: `zsh` — affected >=0 <5.2-r4
- Alpine:v3.6: `zsh` — affected >=0 <5.3.1-r1
- Alpine:v3.7: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.8: `zsh` — affected >=0 <5.4.2-r1
- Alpine:v3.9: `zsh` — affected >=0 <5.4.2-r1

## Details
zsh through version 5.4.2 is vulnerable to a stack-based buffer overflow in the exec.c:hashcmd() function. A local attacker could exploit this to cause a denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1071
