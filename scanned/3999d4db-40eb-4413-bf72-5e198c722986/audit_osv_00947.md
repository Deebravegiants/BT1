# [M] ALPINE-CVE-2018-12384

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-12384
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12384
Type: osv

## Affected
- Alpine:v3.10: `nss` — affected >=0 <3.39-r0
- Alpine:v3.11: `nss` — affected >=0 <3.39-r0
- Alpine:v3.12: `nss` — affected >=0 <3.39-r0
- Alpine:v3.19: `nss` — affected >=0 <3.39-r0
- Alpine:v3.20: `nss` — affected >=0 <3.39-r0
- Alpine:v3.21: `nss` — affected >=0 <3.39-r0
- Alpine:v3.22: `nss` — affected >=0 <3.39-r0
- Alpine:v3.23: `nss` — affected >=0 <3.39-r0
- Alpine:v3.24: `nss` — affected >=0 <3.39-r0
- Alpine:v3.8: `nss` — affected >=0 <3.36.1-r1
- Alpine:v3.9: `nss` — affected >=0 <3.39-r0

## Details
When handling a SSLv2-compatible ClientHello request, the server doesn't generate a new random value but sends an all-zero value instead. This results in full malleability of the ClientHello for SSLv2 used for TLS 1.2 in all versions prior to NSS 3.39. This does not impact TLS 1.3.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12384
