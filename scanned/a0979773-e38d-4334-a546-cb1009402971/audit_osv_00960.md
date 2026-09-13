# [M] ALPINE-CVE-2018-1301

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-1301
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1301
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.4: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.5: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.6: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.7: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.8: `apache2` — affected >=0 <2.4.33-r0
- Alpine:v3.9: `apache2` — affected >=0 <2.4.33-r0

## Details
A specially crafted request could have crashed the Apache HTTP Server prior to version 2.4.30, due to an out of bound access after a size limit is reached by reading the HTTP header. This vulnerability is considered very hard if not impossible to trigger in non-debug mode (both log and build level), so it is classified as low risk for common server usage.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1301
