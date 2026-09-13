# [H] ALPINE-CVE-2022-29458

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-29458
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2022-04-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-29458
Type: osv

## Affected
- Alpine:v3.13: `ncurses` — affected >=0 <6.2_p20210109-r1
- Alpine:v3.14: `ncurses` — affected >=0 <6.2_p20210612-r1
- Alpine:v3.15: `ncurses` — affected >=0 <6.3_p20211120-r1
- Alpine:v3.16: `ncurses` — affected >=0 <6.3_p20220416-r0
- Alpine:v3.17: `ncurses` — affected >=0 <6.3_p20220416-r0
- Alpine:v3.18: `ncurses` — affected >=0 <6.3_p20220416-r0
- Alpine:v3.19: `ncurses` — affected >=0 <6.3_p20220416-r0
- Alpine:v3.20: `ncurses` — affected >=0 <6.3_p20220416-r0
- Alpine:v3.21: `ncurses` — affected >=0 <6.3_p20220416-r0
- Alpine:v3.22: `ncurses` — affected >=0 <6.3_p20220416-r0
- Alpine:v3.23: `ncurses` — affected >=0 <6.3_p20220416-r0
- Alpine:v3.24: `ncurses` — affected >=0 <6.3_p20220416-r0

## Details
ncurses 6.3 before patch 20220416 has an out-of-bounds read and segmentation violation in convert_strings in tinfo/read_entry.c in the terminfo library.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-29458
