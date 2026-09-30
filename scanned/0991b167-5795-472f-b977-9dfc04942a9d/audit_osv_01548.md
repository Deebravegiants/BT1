# [M] ALPINE-CVE-2019-20372

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-20372
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-01-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-20372
Type: osv

## Affected
- Alpine:v3.10: `nginx` — affected >=0 <1.16.1-r2
- Alpine:v3.11: `nginx` — affected >=0 <1.16.1-r6
- Alpine:v3.12: `nginx` — affected >=0 <1.16.1-r6
- Alpine:v3.13: `nginx` — affected >=0 <1.16.1-r6
- Alpine:v3.14: `nginx` — affected >=0 <1.16.1-r6
- Alpine:v3.15: `nginx` — affected >=0 <1.16.1-r6
- Alpine:v3.16: `nginx` — affected >=0 <1.16.1-r6
- Alpine:v3.17: `nginx` — affected >=0 <1.16.1-r6
- Alpine:v3.18: `nginx` — affected >=0 <1.16.1-r6
- Alpine:v3.19: `nginx` — affected >=0 <1.16.1-r6
- Alpine:v3.20: `nginx` — affected >=0 <1.16.1-r6
- Alpine:v3.21: `nginx` — affected >=0 <1.16.1-r6
- Alpine:v3.22: `nginx` — affected >=0 <1.16.1-r6
- Alpine:v3.23: `nginx` — affected >=0 <1.16.1-r6
- Alpine:v3.24: `nginx` — affected >=0 <1.16.1-r6
- Alpine:v3.8: `nginx` — affected >=0 <1.14.2-r2
- Alpine:v3.9: `nginx` — affected >=0 <1.14.2-r5

## Details
NGINX before 1.17.7, with certain error_page configurations, allows HTTP request smuggling, as demonstrated by the ability of an attacker to read unauthorized web pages in environments where NGINX is being fronted by a load balancer.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-20372
