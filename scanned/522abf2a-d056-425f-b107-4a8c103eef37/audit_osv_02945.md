# [M] ALPINE-CVE-2023-5388

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-5388
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2024-03-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-5388
Type: osv

## Affected
- Alpine:v3.19: `nss` — affected >=0 <3.98-r0
- Alpine:v3.20: `nss` — affected >=0 <3.98-r0
- Alpine:v3.21: `nss` — affected >=0 <3.98-r0
- Alpine:v3.22: `nss` — affected >=0 <3.98-r0
- Alpine:v3.23: `nss` — affected >=0 <3.98-r0
- Alpine:v3.24: `nss` — affected >=0 <3.98-r0

## Details
NSS was susceptible to a timing side-channel attack when performing RSA decryption. This attack could potentially allow an attacker to recover the private data. This vulnerability affects Firefox < 124, Firefox ESR < 115.9, and Thunderbird < 115.9.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-5388
