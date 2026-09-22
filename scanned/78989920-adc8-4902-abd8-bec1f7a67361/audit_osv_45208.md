# [M] The ECDSA signature implementation in ecdsa.c in Arm Mbed Crypto 2.1 and Mbed TLS through 2.19.1...

## Summary
Severity: Medium
Advisory: JLSEC-2025-199
Ecosystem: Julia
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/JLSEC-2025-199
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=0 <2.16.6+0

## Details
The ECDSA signature implementation in ecdsa.c in Arm Mbed Crypto 2.1 and Mbed TLS through 2.19.1 does not reduce the blinded scalar before computing the inverse, which allows a local attacker to recover the private key via side-channel attacks.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A3GWQNONS7GRORXZJ7MOJFUEJ2ZJ4OUW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NGDACU65MYZXXVPQP2EBHUJGOR4RWLVY/
- https://tls.mbed.org/tech-updates/security-advisories
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2019-12
