# [H] ALPINE-CVE-2019-10081

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-10081
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10081
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
HTTP/2 (2.4.20 through 2.4.39) very early pushes, for example configured with "H2PushResource", could lead to an overwrite of memory in the pushing request's pool, leading to crashes. The memory copied is that of the configured push link header values, not data supplied by the client.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10081
