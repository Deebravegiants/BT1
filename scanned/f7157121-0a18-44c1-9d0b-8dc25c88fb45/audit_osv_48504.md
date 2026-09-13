# [H] CVE-2017-8821

## Summary
Severity: High
Advisory: CVE-2017-8821
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-03
Source: https://osv.dev/vulnerability/CVE-2017-8821
Type: osv

## Details
In Tor before 0.2.5.16, 0.2.6 through 0.2.8 before 0.2.8.17, 0.2.9 before 0.2.9.14, 0.3.0 before 0.3.0.13, and 0.3.1 before 0.3.1.9, an attacker can cause a denial of service (application hang) via crafted PEM input that signifies a public key requiring a password, which triggers an attempt by the OpenSSL library to ask the user for the password, aka TROVE-2017-011.

## References
- https://blog.torproject.org/new-stable-tor-releases-security-fixes-0319-03013-02914-02817-02516
- https://bugs.torproject.org/24246
- https://www.debian.org/security/2017/dsa-4054
