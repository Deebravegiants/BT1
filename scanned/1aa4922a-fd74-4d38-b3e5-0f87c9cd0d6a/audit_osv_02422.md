# [C] ALPINE-CVE-2022-22721

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-22721
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-03-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-22721
Type: osv

## Affected
- Alpine:v3.12: `apache2` — affected >=0 <2.4.53-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.53-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.53-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.53-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.53-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.53-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.53-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.53-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.53-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.53-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.53-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.53-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.53-r0

## Details
If LimitXMLRequestBody is set to allow request bodies larger than 350MB (defaults to 1M) on 32 bit systems an integer overflow happens which later causes out of bounds writes. This issue affects Apache HTTP Server 2.4.52 and earlier.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-22721
