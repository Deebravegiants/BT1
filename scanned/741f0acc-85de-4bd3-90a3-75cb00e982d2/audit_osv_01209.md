# [H] ALPINE-CVE-2018-5764

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-5764
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-01-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5764
Type: osv

## Affected
- Alpine:v3.4: `rsync` — affected >=0 <3.1.3-r0
- Alpine:v3.5: `rsync` — affected >=0 <3.1.3-r0
- Alpine:v3.6: `rsync` — affected >=0 <3.1.3-r0
- Alpine:v3.7: `rsync` — affected >=0 <3.1.3-r0

## Details
The parse_arguments function in options.c in rsyncd in rsync before 3.1.3 does not prevent multiple --protect-args uses, which allows remote attackers to bypass an argument-sanitization protection mechanism.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5764
