# [M] An issue was discovered in Arm Mbed TLS before 2.16.6 and 2.7.x before 2.7.15

## Summary
Severity: Medium
Advisory: JLSEC-2025-201
Ecosystem: Julia
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/JLSEC-2025-201
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=0 <2.16.6+0

## Details
An issue was discovered in Arm Mbed TLS before 2.16.6 and 2.7.x before 2.7.15. An attacker that can get precise enough side-channel measurements can recover the long-term ECDSA private key by (1) reconstructing the projective coordinate of the result of scalar multiplication by exploiting side channels in the conversion to affine coordinates; (2) using an attack described by Naccache, Smart, and Stern in 2003 to recover a few bits of the ephemeral scalar from those projective coordinates via several measurements; and (3) using a lattice attack to get from there to the long-term ECDSA private key used for the signatures. Typically an attacker would have sufficient access when attacking an SGX enclave and controlling the untrusted OS.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FCWN5HIF4CJ2LZTOMEBJ7Q4IMMV7ZU2V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZNOS2IIBH5WNJXZUV546PY7666DE7Y3L/
- https://tls.mbed.org/tech-updates/releases/mbedtls-2.16.6-and-2.7.15-released
- https://tls.mbed.org/tech-updates/security-advisories
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2020-04
