# [C] ALPINE-CVE-2017-10684

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-10684
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-10684
Type: osv

## Affected
- Alpine:v3.10: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.11: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.12: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.13: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.14: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.15: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.16: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.17: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.18: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.19: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.20: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.21: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.22: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.23: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.24: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.3: `ncurses` — affected >=0 <6.0-r7
- Alpine:v3.4: `ncurses` — affected >=0 <6.0-r8
- Alpine:v3.5: `ncurses` — affected >=0 <6.0-r8
- Alpine:v3.6: `ncurses` — affected >=0 <6.0-r8
- Alpine:v3.7: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.8: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.9: `ncurses` — affected >=0 <6.0_p20170701-r0

## Details
In ncurses 6.0, there is a stack-based buffer overflow in the fmt_entry function. A crafted input will lead to a remote arbitrary code execution attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-10684
