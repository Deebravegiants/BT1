# [H] ALPINE-CVE-2022-4141

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-4141
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-11-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-4141
Type: osv

## Affected
- Alpine:v3.17: `vim` — affected >=0 <9.0.0999-r0
- Alpine:v3.18: `vim` — affected >=0 <9.0.0999-r0
- Alpine:v3.19: `vim` — affected >=0 <9.0.0999-r0
- Alpine:v3.20: `vim` — affected >=0 <9.0.0999-r0
- Alpine:v3.21: `vim` — affected >=0 <9.0.0999-r0
- Alpine:v3.22: `vim` — affected >=0 <9.0.0999-r0
- Alpine:v3.23: `vim` — affected >=0 <9.0.0999-r0

## Details
Heap based buffer overflow in vim/vim 9.0.0946 and below by allowing an attacker to CTRL-W gf in the expression used in the RHS of the substitute command.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-4141
