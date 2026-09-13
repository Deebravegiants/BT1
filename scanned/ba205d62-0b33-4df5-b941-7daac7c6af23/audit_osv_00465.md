# [H] ALPINE-CVE-2017-13728

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-13728
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-13728
Type: osv

## Affected
- Alpine:v3.3: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.4: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.5: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.6: `ncurses` — affected >=0 <6.0_p20170930-r0

## Details
There is an infinite loop in the next_char function in comp_scan.c in ncurses 6.0, related to libtic. A crafted input will lead to a remote denial of service attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-13728
