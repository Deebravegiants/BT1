# [C] ALPINE-CVE-2021-44790

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-44790
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-44790
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
A carefully crafted request body can cause a buffer overflow in the mod_lua multipart parser (r:parsebody() called from Lua scripts). The Apache httpd team is not aware of an exploit for the vulnerabilty though it might be possible to craft one. This issue affects Apache HTTP Server 2.4.51 and earlier.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-44790
