# [M] ALPINE-CVE-2020-6829

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-6829
Ecosystem: Alpine:v3.12, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-10-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-6829
Type: osv

## Affected
- Alpine:v3.12: `nss` — affected >=0 <3.55-r0
- Alpine:v3.19: `nss` — affected >=0 <3.55-r0
- Alpine:v3.20: `nss` — affected >=0 <3.55-r0
- Alpine:v3.21: `nss` — affected >=0 <3.55-r0
- Alpine:v3.22: `nss` — affected >=0 <3.55-r0
- Alpine:v3.23: `nss` — affected >=0 <3.55-r0
- Alpine:v3.24: `nss` — affected >=0 <3.55-r0

## Details
When performing EC scalar point multiplication, the wNAF point multiplication algorithm was used; which leaked partial information about the nonce used during signature generation. Given an electro-magnetic trace of a few signature generations, the private key could have been computed. This vulnerability affects Firefox < 80 and Firefox for Android < 80.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-6829
