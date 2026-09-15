# [C] ALPINE-CVE-2017-10685

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-10685
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-10685
Type: osv

## Affected
- Alpine:v3.3: `ncurses` — affected >=0 <6.0-r7
- Alpine:v3.4: `ncurses` — affected >=0 <6.0-r8
- Alpine:v3.5: `ncurses` — affected >=0 <6.0-r8
- Alpine:v3.6: `ncurses` — affected >=0 <6.0-r8

## Details
In ncurses 6.0, there is a format string vulnerability in the fmt_entry function. A crafted input will lead to a remote arbitrary code execution attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-10685
