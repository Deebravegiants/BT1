# [M] CVE-2018-0498

## Summary
Severity: Medium
Advisory: CVE-2018-0498
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-28
Source: https://osv.dev/vulnerability/CVE-2018-0498
Type: osv

## Details
ARM mbed TLS before 2.12.0, before 2.7.5, and before 2.1.14 allows local users to achieve partial plaintext recovery (for a CBC based ciphersuite) via a cache-based side-channel attack.

## References
- https://usn.ubuntu.com/4267-1/
- https://lists.debian.org/debian-lts-announce/2018/09/msg00029.html
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2018-02
- https://www.debian.org/security/2018/dsa-4296
