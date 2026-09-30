# [M] ALPINE-CVE-2018-1302

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-1302
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1302
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
When an HTTP/2 stream was destroyed after being handled, the Apache HTTP Server prior to version 2.4.30 could have written a NULL pointer potentially to an already freed memory. The memory pools maintained by the server make this vulnerability hard to trigger in usual configurations, the reporter and the team could not reproduce it outside debug builds, so it is classified as low risk.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1302
