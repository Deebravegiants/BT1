# [M] ALPINE-CVE-2018-0494

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-0494
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-05-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-0494
Type: osv

## Affected
- Alpine:v3.10: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.11: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.12: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.13: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.14: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.15: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.16: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.17: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.18: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.19: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.20: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.21: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.22: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.23: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.24: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.4: `wget` — affected >=0 <1.18-r3
- Alpine:v3.5: `wget` — affected >=0 <1.18-r4
- Alpine:v3.6: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.7: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.8: `wget` — affected >=0 <1.19.5-r0
- Alpine:v3.9: `wget` — affected >=0 <1.19.5-r0

## Details
GNU Wget before 1.19.5 is prone to a cookie injection vulnerability in the resp_new function in http.c via a \r\n sequence in a continuation line.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-0494
