# [H] ALPINE-CVE-2021-44224

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-44224
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2021-12-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-44224
Type: osv

## Affected
- Alpine:v3.12: `apache2` — affected >=0 <2.4.52-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.52-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.52-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.52-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.52-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.52-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.52-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.52-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.52-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.52-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.52-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.52-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.52-r0

## Details
A crafted URI sent to httpd configured as a forward proxy (ProxyRequests on) can cause a crash (NULL pointer dereference) or, for configurations mixing forward and reverse proxy declarations, can allow for requests to be directed to a declared Unix Domain Socket endpoint (Server Side Request Forgery). This issue affects Apache HTTP Server 2.4.7 up to 2.4.51 (included).

## References
- https://security.alpinelinux.org/vuln/CVE-2021-44224
