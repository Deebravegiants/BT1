# [H] ALPINE-CVE-2018-1333

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1333
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1333
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.5: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.6: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.7: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.8: `apache2` — affected >=0 <2.4.34-r0
- Alpine:v3.9: `apache2` — affected >=0 <2.4.34-r0

## Details
By specially crafting HTTP/2 requests, workers would be allocated 60 seconds longer than necessary, leading to worker exhaustion and a denial of service. Fixed in Apache HTTP Server 2.4.34 (Affected 2.4.18-2.4.30,2.4.33).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1333
