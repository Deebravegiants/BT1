# [M] ALPINE-CVE-2020-10932

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-10932
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-10932
Type: osv

## Affected
- Alpine:v3.10: `mbedtls` — affected >=0 <2.16.6-r0
- Alpine:v3.11: `mbedtls` — affected >=0 <2.16.6-r0
- Alpine:v3.12: `mbedtls` — affected >=0 <2.16.6-r0
- Alpine:v3.13: `mbedtls` — affected >=0 <2.16.6-r0
- Alpine:v3.14: `mbedtls` — affected >=0 <2.16.6-r0
- Alpine:v3.15: `mbedtls` — affected >=0 <2.16.6-r0
- Alpine:v3.16: `mbedtls` — affected >=0 <2.16.6-r0
- Alpine:v3.17: `mbedtls` — affected >=0 <2.16.6-r0
- Alpine:v3.18: `mbedtls` — affected >=0 <2.16.6-r0
- Alpine:v3.19: `mbedtls` — affected >=0 <2.16.6-r0
- Alpine:v3.20: `mbedtls` — affected >=0 <2.16.6-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <2.16.6-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <2.16.6-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <2.16.6-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <2.16.6-r0

## Details
An issue was discovered in Arm Mbed TLS before 2.16.6 and 2.7.x before 2.7.15. An attacker that can get precise enough side-channel measurements can recover the long-term ECDSA private key by (1) reconstructing the projective coordinate of the result of scalar multiplication by exploiting side channels in the conversion to affine coordinates; (2) using an attack described by Naccache, Smart, and Stern in 2003 to recover a few bits of the ephemeral scalar from those projective coordinates via several measurements; and (3) using a lattice attack to get from there to the long-term ECDSA private key used for the signatures. Typically an attacker would have sufficient access when attacking an SGX enclave and controlling the untrusted OS.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-10932
