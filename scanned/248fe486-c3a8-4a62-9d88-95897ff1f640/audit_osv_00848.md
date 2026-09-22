# [M] ALPINE-CVE-2018-0495

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-0495
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-0495
Type: osv

## Affected
- Alpine:v3.10: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.11: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.12: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.13: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.14: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.15: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.16: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.17: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.18: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.19: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.20: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.21: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.22: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.23: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.24: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.5: `libgcrypt` — affected >=1.8.0 <1.7.10-r0
- Alpine:v3.6: `libgcrypt` — affected >=1.8.0 <1.7.10-r0
- Alpine:v3.7: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.8: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.9: `libgcrypt` — affected >=1.8.0 <1.8.3-r0
- Alpine:v3.10: `libressl` — affected >=0 <2.7.4-r0
- Alpine:v3.11: `libressl` — affected >=0 <2.7.4-r0
- Alpine:v3.12: `libressl` — affected >=0 <2.7.4-r0
- Alpine:v3.13: `libressl` — affected >=0 <2.7.4-r0
- Alpine:v3.7: `libressl` — affected >=0 <2.6.5-r0

## Details
Libgcrypt before 1.7.10 and 1.8.x before 1.8.3 allows a memory-cache side-channel attack on ECDSA signatures that can be mitigated through the use of blinding during the signing process in the _gcry_ecc_ecdsa_sign function in cipher/ecc-ecdsa.c, aka the Return Of the Hidden Number Problem or ROHNP. To discover an ECDSA key, the attacker needs access to either the local machine or a different virtual machine on the same physical host.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-0495
