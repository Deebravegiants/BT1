# [H] ALPINE-CVE-2020-13950

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-13950
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-13950
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.48-r0

## Details
Apache HTTP Server versions 2.4.41 to 2.4.46 mod_proxy_http can be made to crash (NULL pointer dereference) with specially crafted requests using both Content-Length and Transfer-Encoding headers, leading to a Denial of Service

## References
- https://security.alpinelinux.org/vuln/CVE-2020-13950
