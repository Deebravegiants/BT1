# [C] CVE-2018-0488

## Summary
Severity: Critical
Advisory: CVE-2018-0488
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/CVE-2018-0488
Type: osv

## Details
ARM mbed TLS before 1.3.22, before 2.1.10, and before 2.7.0, when the truncated HMAC extension and CBC are used, allows remote attackers to execute arbitrary code or cause a denial of service (heap corruption) via a crafted application packet within a TLS or DTLS session.

## References
- https://usn.ubuntu.com/4267-1/
- http://www.securityfocus.com/bid/103057
- https://security.gentoo.org/glsa/201804-19
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2018-01
- https://www.debian.org/security/2018/dsa-4138
- https://www.debian.org/security/2018/dsa-4147
