# [M] ALPINE-CVE-2017-8301

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-8301
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2017-04-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-8301
Type: osv

## Affected
- Alpine:v3.10: `libressl` — affected >=0 <2.5.3-r1
- Alpine:v3.11: `libressl` — affected >=0 <2.5.3-r1
- Alpine:v3.12: `libressl` — affected >=0 <2.5.3-r1
- Alpine:v3.13: `libressl` — affected >=0 <2.5.3-r1
- Alpine:v3.6: `libressl` — affected >=0 <2.5.3-r1
- Alpine:v3.7: `libressl` — affected >=0 <2.5.3-r1
- Alpine:v3.8: `libressl` — affected >=0 <2.5.3-r1
- Alpine:v3.9: `libressl` — affected >=0 <2.5.3-r1

## Details
LibreSSL 2.5.1 to 2.5.3 lacks TLS certificate verification if SSL_get_verify_result is relied upon for a later check of a verification result, in a use case where a user-provided verification callback returns 1, as demonstrated by acceptance of invalid certificates by nginx.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-8301
