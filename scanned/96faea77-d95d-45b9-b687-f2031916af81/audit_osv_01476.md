# [H] ALPINE-CVE-2019-16056

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-16056
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-16056
Type: osv

## Affected
- Alpine:v3.11: `python2` — affected >=0 <2.7.16-r3
- Alpine:v3.12: `python2` — affected >=0 <2.7.16-r3
- Alpine:v3.10: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.11: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.12: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.13: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.14: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.15: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.16: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.17: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.18: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.19: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.20: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.21: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.22: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.23: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.24: `python3` — affected >=0 <3.7.5-r0
- Alpine:v3.7: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.8: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.9: `python3` — affected >=0 <3.6.9-r1

## Details
An issue was discovered in Python through 2.7.16, 3.x through 3.5.7, 3.6.x through 3.6.9, and 3.7.x through 3.7.4. The email module wrongly parses email addresses that contain multiple @ characters. An application that uses the email module and implements some kind of checks on the From/To headers of a message could be tricked into accepting an email address that should be denied. An attack may be the same as in CVE-2019-11340; however, this CVE applies to Python more generally.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-16056
