# [M] ALPINE-CVE-2017-13734

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-13734
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-13734
Type: osv

## Affected
- Alpine:v3.3: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.4: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.5: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.6: `ncurses` — affected >=0 <6.0_p20170930-r0

## Details
There is an illegal address access in the _nc_safe_strcat function in strings.c in ncurses 6.0 that will lead to a remote denial of service attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-13734
