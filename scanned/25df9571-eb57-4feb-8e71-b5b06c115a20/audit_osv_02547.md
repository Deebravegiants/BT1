# [H] ALPINE-CVE-2022-30522

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-30522
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-30522
Type: osv

## Affected
- Alpine:v3.13: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.54-r0

## Details
If Apache HTTP Server 2.4.53 is configured to do transformations with mod_sed in contexts where the input to mod_sed may be very large, mod_sed may make excessively large memory allocations and trigger an abort.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-30522
