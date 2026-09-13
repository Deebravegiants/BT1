# [H] CVE-2017-14032

## Summary
Severity: High
Advisory: CVE-2017-14032
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2017-14032
Type: osv

## Details
ARM mbed TLS before 1.3.21 and 2.x before 2.1.9, if optional authentication is configured, allows remote attackers to bypass peer authentication via an X.509 certificate chain with many intermediates. NOTE: although mbed TLS was formerly known as PolarSSL, the releases shipped with the PolarSSL name are not affected.

## References
- http://www.debian.org/security/2017/dsa-3967
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2017-02
- https://bugs.debian.org/873557
- https://github.com/ARMmbed/mbedtls/commit/31458a18788b0cf0b722acda9bb2f2fe13a3fb32
- https://github.com/ARMmbed/mbedtls/commit/d15795acd5074e0b44e71f7ede8bdfe1b48591fc
