# [H] ALPINE-CVE-2018-1083

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1083
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1083
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
Zsh before version 5.4.2-test-1 is vulnerable to a buffer overflow in the shell autocomplete functionality. A local unprivileged user can create a specially crafted directory path which leads to code execution in the context of the user who tries to use autocomplete to traverse the before mentioned path. If the user affected is privileged, this leads to privilege escalation.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1083
