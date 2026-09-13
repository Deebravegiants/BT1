# [H] ALPINE-CVE-2017-7529

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7529
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7529
Type: osv

## Affected
- Alpine:v3.10: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.11: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.12: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.13: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.14: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.15: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.16: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.17: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.18: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.19: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.20: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.21: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.22: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.23: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.24: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.4: `nginx` — affected >=0.5.6 <1.10.3-r0
- Alpine:v3.5: `nginx` — affected >=0.5.6 <1.10.3-r1
- Alpine:v3.6: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.7: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.8: `nginx` — affected >=0.5.6 <1.12.1-r0
- Alpine:v3.9: `nginx` — affected >=0.5.6 <1.12.1-r0

## Details
Nginx versions since 0.5.6 up to and including 1.13.2 are vulnerable to integer overflow vulnerability in nginx range filter module resulting into leak of potentially sensitive information triggered by specially crafted request.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7529
