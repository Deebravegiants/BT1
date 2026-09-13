# [M] ALPINE-CVE-2018-0734

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-0734
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-10-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-0734
Type: osv

## Affected
- Alpine:v3.10: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.11: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.12: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.13: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.14: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.15: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.16: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.17: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.18: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.19: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.20: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.21: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.22: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.9: `nodejs` — affected >=0 <10.14.0-r0
- Alpine:v3.10: `openssl` — affected >=1.0.2 <1.1.1a-r0
- Alpine:v3.11: `openssl` — affected >=1.0.2 <1.1.1a-r0
- Alpine:v3.12: `openssl` — affected >=1.0.2 <1.1.1a-r0
- Alpine:v3.13: `openssl` — affected >=1.0.2 <1.1.1a-r0
- Alpine:v3.14: `openssl` — affected >=1.0.2 <1.1.1a-r0
- Alpine:v3.15: `openssl` — affected >=1.0.2 <1.1.1a-r0
- Alpine:v3.16: `openssl` — affected >=1.0.2 <1.1.1a-r0
- Alpine:v3.17: `openssl` — affected >=1.0.2 <1.1.1a-r0
- Alpine:v3.18: `openssl` — affected >=1.0.2 <1.1.1a-r0

## Details
The OpenSSL DSA signature algorithm has been shown to be vulnerable to a timing side channel attack. An attacker could use variations in the signing algorithm to recover the private key. Fixed in OpenSSL 1.1.1a (Affected 1.1.1). Fixed in OpenSSL 1.1.0j (Affected 1.1.0-1.1.0i). Fixed in OpenSSL 1.0.2q (Affected 1.0.2-1.0.2p).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-0734
