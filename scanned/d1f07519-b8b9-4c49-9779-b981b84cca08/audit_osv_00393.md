# [H] ALPINE-CVE-2017-11112

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-11112
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11112
Type: osv

## Affected
- Alpine:v3.3: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.4: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.5: `ncurses` — affected >=0 <6.0_p20170701-r0
- Alpine:v3.6: `ncurses` — affected >=0 <6.0_p20170930-r0

## Details
In ncurses 6.0, there is an attempted 0xffffffffffffffff access in the append_acs function of tinfo/parse_entry.c. It could lead to a remote denial of service attack if the terminfo library code is used to process untrusted terminfo data.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11112
