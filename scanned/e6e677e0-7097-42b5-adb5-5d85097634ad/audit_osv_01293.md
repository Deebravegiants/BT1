# [H] ALPINE-CVE-2018-9860

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-9860
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-9860
Type: osv

## Affected
- Alpine:v3.11: `botan` — affected >=1.11.32 <2.6.0-r0
- Alpine:v3.12: `botan` — affected >=1.11.32 <2.6.0-r0
- Alpine:v3.13: `botan` — affected >=1.11.32 <2.6.0-r0
- Alpine:v3.14: `botan` — affected >=1.11.32 <2.6.0-r0
- Alpine:v3.15: `botan` — affected >=1.11.32 <2.6.0-r0
- Alpine:v3.16: `botan` — affected >=1.11.32 <2.6.0-r0
- Alpine:v3.17: `botan` — affected >=1.11.32 <2.6.0-r0
- Alpine:v3.18: `botan` — affected >=1.11.32 <2.6.0-r0
- Alpine:v3.19: `botan` — affected >=1.11.32 <2.6.0-r0
- Alpine:v3.20: `botan` — affected >=1.11.32 <2.6.0-r0
- Alpine:v3.21: `botan` — affected >=1.11.32 <2.6.0-r0

## Details
An issue was discovered in Botan 1.11.32 through 2.x before 2.6.0. An off-by-one error when processing malformed TLS-CBC ciphertext could cause the receiving side to include in the HMAC computation exactly 64K bytes of data following the record buffer, aka an over-read. The MAC comparison will subsequently fail and the connection will be closed. This could be used for denial of service. No information leak occurs.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-9860
