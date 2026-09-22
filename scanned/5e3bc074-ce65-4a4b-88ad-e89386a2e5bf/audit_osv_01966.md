# [H] ALPINE-CVE-2020-35452

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-35452
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2021-06-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-35452
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
Apache HTTP Server versions 2.4.0 to 2.4.46 A specially crafted Digest nonce can cause a stack overflow in mod_auth_digest. There is no report of this overflow being exploitable, nor the Apache HTTP Server team could create one, though some particular compiler and/or compilation option might make it possible, with limited consequences anyway due to the size (a single byte) and the value (zero byte) of the overflow

## References
- https://security.alpinelinux.org/vuln/CVE-2020-35452
