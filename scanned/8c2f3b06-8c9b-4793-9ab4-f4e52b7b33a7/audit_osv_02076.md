# [H] ALPINE-CVE-2021-20305

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-20305
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-20305
Type: osv

## Affected
- Alpine:v3.13: `nettle` — affected >=0 <3.7.2-r0
- Alpine:v3.14: `nettle` — affected >=0 <3.7.2-r0
- Alpine:v3.15: `nettle` — affected >=0 <3.7.2-r0
- Alpine:v3.16: `nettle` — affected >=0 <3.7.2-r0
- Alpine:v3.17: `nettle` — affected >=0 <3.7.2-r0
- Alpine:v3.18: `nettle` — affected >=0 <3.7.2-r0
- Alpine:v3.19: `nettle` — affected >=0 <3.7.2-r0
- Alpine:v3.20: `nettle` — affected >=0 <3.7.2-r0
- Alpine:v3.21: `nettle` — affected >=0 <3.7.2-r0
- Alpine:v3.22: `nettle` — affected >=0 <3.7.2-r0
- Alpine:v3.23: `nettle` — affected >=0 <3.7.2-r0
- Alpine:v3.24: `nettle` — affected >=0 <3.7.2-r0

## Details
A flaw was found in Nettle in versions before 3.7.2, where several Nettle signature verification functions (GOST DSA, EDDSA & ECDSA) result in the Elliptic Curve Cryptography point (ECC) multiply function being called with out-of-range scalers, possibly resulting in incorrect results. This flaw allows an attacker to force an invalid signature, causing an assertion failure or possible validation. The highest threat to this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-20305
