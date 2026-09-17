# [M] Arm Mbed TLS before 2.19.0 and Arm Mbed Crypto before 2.0.0, when deterministic ECDSA is enabled,...

## Summary
Severity: Medium
Advisory: JLSEC-2025-198
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/JLSEC-2025-198
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=0 <2.16.6+0

## Details
Arm Mbed TLS before 2.19.0 and Arm Mbed Crypto before 2.0.0, when deterministic ECDSA is enabled, use an RNG with insufficient entropy for blinding, which might allow an attacker to recover a private key via side-channel attacks if a victim signs the same message many times. (For Mbed TLS, the fix is also available in versions 2.7.12 and 2.16.3.)

## References
- https://github.com/ARMmbed/mbedtls/commit/298a43a77ec0ed2c19a8c924ddd8571ef3e65dfd
- https://github.com/ARMmbed/mbedtls/commit/33f66ba6fd234114aa37f0209dac031bb2870a9b
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CGSKQSGR5SOBRBXDSSPTCDSBB5K3GMPF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CSFFOROD6IVLADZHNJC2LPDV7FQRP7XB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PEHHH2DOBXB25CAU3Q6E66X723VAYTB5/
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2019-10
