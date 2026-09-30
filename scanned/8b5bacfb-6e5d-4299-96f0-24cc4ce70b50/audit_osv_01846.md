# [M] ALPINE-CVE-2020-1927

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-1927
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-04-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-1927
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.8: `apache2` — affected >=0 <2.4.43-r0
- Alpine:v3.9: `apache2` — affected >=0 <2.4.43-r0

## Details
In Apache HTTP Server 2.4.0 to 2.4.41, redirects configured with mod_rewrite that were intended to be self-referential might be fooled by encoded newlines and redirect instead to an an unexpected URL within the request URL.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-1927
