# [C] ALPINE-CVE-2019-10082

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-10082
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-09-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10082
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.7: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.8: `apache2` — affected >=0 <2.4.41-r0
- Alpine:v3.9: `apache2` — affected >=0 <2.4.41-r0

## Details
In Apache HTTP Server 2.4.18-2.4.39, using fuzzed network input, the http/2 session handling could be made to read memory after being freed, during connection shutdown.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10082
