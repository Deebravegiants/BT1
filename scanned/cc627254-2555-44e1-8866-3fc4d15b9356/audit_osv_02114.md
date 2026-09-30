# [C] ALPINE-CVE-2021-24115

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-24115
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-24115
Type: osv

## Affected
- Alpine:v3.11: `botan` — affected >=0 <2.11.0-r4
- Alpine:v3.12: `botan` — affected >=0 <2.11.0-r6
- Alpine:v3.13: `botan` — affected >=0 <2.11.0-r6
- Alpine:v3.14: `botan` — affected >=0 <2.17.3-r0
- Alpine:v3.15: `botan` — affected >=0 <2.17.3-r0
- Alpine:v3.16: `botan` — affected >=0 <2.17.3-r0
- Alpine:v3.17: `botan` — affected >=0 <2.17.3-r0
- Alpine:v3.18: `botan` — affected >=0 <2.17.3-r0
- Alpine:v3.19: `botan` — affected >=0 <2.17.3-r0
- Alpine:v3.20: `botan` — affected >=0 <2.17.3-r0
- Alpine:v3.21: `botan` — affected >=0 <2.17.3-r0

## Details
In Botan before 2.17.3, constant-time computations are not used for certain decoding and encoding operations (base32, base58, base64, and hex).

## References
- https://security.alpinelinux.org/vuln/CVE-2021-24115
