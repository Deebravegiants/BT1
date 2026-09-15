# [H] ALPINE-CVE-2023-29491

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-29491
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-29491
Type: osv

## Affected
- Alpine:v3.15: `ncurses` — affected >=0 <6.3_p20211120-r2
- Alpine:v3.16: `ncurses` — affected >=0 <6.3_p20220521-r1
- Alpine:v3.17: `ncurses` — affected >=0 <6.3_p20221119-r1
- Alpine:v3.19: `ncurses` — affected >=0 <6.4_p20230424-r0
- Alpine:v3.20: `ncurses` — affected >=0 <6.4_p20230424-r0
- Alpine:v3.21: `ncurses` — affected >=0 <6.4_p20230424-r0
- Alpine:v3.22: `ncurses` — affected >=0 <6.4_p20230424-r0
- Alpine:v3.23: `ncurses` — affected >=0 <6.4_p20230424-r0
- Alpine:v3.24: `ncurses` — affected >=0 <6.4_p20230424-r0

## Details
ncurses before 6.4 20230408, when used by a setuid application, allows local users to trigger security-relevant memory corruption via malformed data in a terminfo database file that is found in $HOME/.terminfo or reached via the TERMINFO or TERM environment variable.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-29491
