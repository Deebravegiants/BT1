# [H] ALPINE-CVE-2019-0190

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-0190
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-0190
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.6: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.7: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.8: `apache2` — affected >=0 <2.4.38-r0
- Alpine:v3.9: `apache2` — affected >=0 <2.4.38-r0

## Details
A bug exists in the way mod_ssl handled client renegotiations. A remote attacker could send a carefully crafted request that would cause mod_ssl to enter a loop leading to a denial of service. This bug can be only triggered with Apache HTTP Server version 2.4.37 when using OpenSSL version 1.1.1 or later, due to an interaction in changes to handling of renegotiation attempts.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-0190
