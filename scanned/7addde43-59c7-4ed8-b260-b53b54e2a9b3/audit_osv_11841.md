# [C] CVE-2018-0487

## Summary
Severity: Critical
Advisory: CVE-2018-0487
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/CVE-2018-0487
Type: osv

## Details
ARM mbed TLS before 1.3.22, before 2.1.10, and before 2.7.0 allows remote attackers to execute arbitrary code or cause a denial of service (buffer overflow) via a crafted certificate chain that is mishandled during RSASSA-PSS signature verification within a TLS or DTLS session.

## References
- https://usn.ubuntu.com/4267-1/
- http://www.securityfocus.com/bid/103056
- https://security.gentoo.org/glsa/201804-19
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2018-01
- https://www.debian.org/security/2018/dsa-4138
- https://www.debian.org/security/2018/dsa-4147
