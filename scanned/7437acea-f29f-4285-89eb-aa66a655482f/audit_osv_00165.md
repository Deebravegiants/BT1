# [H] ALPINE-CVE-2016-6321

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-6321
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-12-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6321
Type: osv

## Affected
- Alpine:v3.10: `tar` — affected >=0 <1.29-r1
- Alpine:v3.11: `tar` — affected >=0 <1.29-r1
- Alpine:v3.12: `tar` — affected >=0 <1.29-r1
- Alpine:v3.13: `tar` — affected >=0 <1.29-r1
- Alpine:v3.14: `tar` — affected >=0 <1.29-r1
- Alpine:v3.15: `tar` — affected >=0 <1.29-r1
- Alpine:v3.16: `tar` — affected >=0 <1.29-r1
- Alpine:v3.17: `tar` — affected >=0 <1.29-r1
- Alpine:v3.18: `tar` — affected >=0 <1.29-r1
- Alpine:v3.19: `tar` — affected >=0 <1.29-r1
- Alpine:v3.20: `tar` — affected >=0 <1.29-r1
- Alpine:v3.21: `tar` — affected >=0 <1.29-r1
- Alpine:v3.22: `tar` — affected >=0 <1.29-r1
- Alpine:v3.23: `tar` — affected >=0 <1.29-r1
- Alpine:v3.24: `tar` — affected >=0 <1.29-r1
- Alpine:v3.4: `tar` — affected >=0 <1.29-r1
- Alpine:v3.5: `tar` — affected >=0 <1.29-r1
- Alpine:v3.6: `tar` — affected >=0 <1.29-r1
- Alpine:v3.7: `tar` — affected >=0 <1.29-r1
- Alpine:v3.8: `tar` — affected >=0 <1.29-r1
- Alpine:v3.9: `tar` — affected >=0 <1.29-r1

## Details
Directory traversal vulnerability in the safer_name_suffix function in GNU tar 1.14 through 1.29 might allow remote attackers to bypass an intended protection mechanism and write to arbitrary files via vectors related to improper sanitization of the file_name parameter, aka POINTYFEATHER.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6321
