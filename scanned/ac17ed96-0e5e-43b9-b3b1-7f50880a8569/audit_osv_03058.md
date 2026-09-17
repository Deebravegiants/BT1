# [H] ALPINE-CVE-2024-34703

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-34703
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-34703
Type: osv

## Affected
- Alpine:v3.17: `botan` — affected >=0 <2.19.5-r0
- Alpine:v3.18: `botan` — affected >=0 <2.19.5-r0
- Alpine:v3.19: `botan` — affected >=0 <2.19.5-r0
- Alpine:v3.20: `botan` — affected >=0 <2.19.4-r0
- Alpine:v3.21: `botan` — affected >=0 <2.19.4-r0

## Details
Botan is a C++ cryptography library. X.509 certificates can identify elliptic curves using either an object identifier or using explicit encoding of the parameters. Prior to versions 3.3.0 and 2.19.4, an attacker could present an ECDSA X.509 certificate using explicit encoding where the parameters are very large. The proof of concept used a 16Kbit prime for this purpose. When parsing, the parameter is checked to be prime, causing excessive computation. This was patched in 2.19.4 and 3.3.0 to allow the prime parameter of the elliptic curve to be at most 521 bits. No known workarounds are available. Note that support for explicit encoding of elliptic curve parameters is deprecated in Botan.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-34703
