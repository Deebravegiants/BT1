# [H] ALPINE-CVE-2017-1000368

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-1000368
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.2 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-06-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-1000368
Type: osv

## Affected
- Alpine:v3.10: `sudo` — affected >=0 <1.8.20_p2-r0
- Alpine:v3.11: `sudo` — affected >=0 <1.8.20_p2-r0
- Alpine:v3.12: `sudo` — affected >=0 <1.8.20_p2-r0
- Alpine:v3.13: `sudo` — affected >=0 <1.8.20_p2-r0
- Alpine:v3.14: `sudo` — affected >=0 <1.8.20_p2-r0
- Alpine:v3.15: `sudo` — affected >=0 <1.8.20_p2-r0
- Alpine:v3.7: `sudo` — affected >=0 <1.8.20_p2-r0
- Alpine:v3.8: `sudo` — affected >=0 <1.8.20_p2-r0
- Alpine:v3.9: `sudo` — affected >=0 <1.8.20_p2-r0

## Details
Todd Miller's sudo version 1.8.20p1 and earlier is vulnerable to an input validation (embedded newlines) in the get_process_ttyname() function resulting in information disclosure and command execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-1000368
