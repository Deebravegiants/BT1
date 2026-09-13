# [H] ALPINE-CVE-2021-33477

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-33477
Ecosystem: Alpine:v3.10, Alpine:v3.11
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-33477
Type: osv

## Affected
- Alpine:v3.10: `mrxvt` — affected >=0 <0.5.4-r8
- Alpine:v3.11: `mrxvt` — affected >=0 <0.5.4-r8
- Alpine:v3.10: `rxvt-unicode` — affected >=0 <9.22-r7
- Alpine:v3.11: `rxvt-unicode` — affected >=0 <9.22-r8

## Details
rxvt-unicode 9.22, rxvt 2.7.10, mrxvt 0.5.4, and Eterm 0.9.7 allow (potentially remote) code execution because of improper handling of certain escape sequences (ESC G Q). A response is terminated by a newline.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-33477
