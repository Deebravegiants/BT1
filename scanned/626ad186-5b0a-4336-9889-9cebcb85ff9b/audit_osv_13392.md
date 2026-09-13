# [M] CVE-2018-19608

## Summary
Severity: Medium
Advisory: CVE-2018-19608
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-12-05
Source: https://osv.dev/vulnerability/CVE-2018-19608
Type: osv

## Details
Arm Mbed TLS before 2.14.1, before 2.7.8, and before 2.1.17 allows a local unprivileged attacker to recover the plaintext of RSA decryption, which is used in RSA-without-(EC)DH(E) cipher suites.

## References
- http://cat.eyalro.net/
- https://tls.mbed.org/tech-updates/releases/mbedtls-2.14.1-2.7.8-and-2.1.17-released
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2018-03
