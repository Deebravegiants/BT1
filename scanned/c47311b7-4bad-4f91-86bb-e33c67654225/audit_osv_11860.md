# [M] CVE-2018-0735

## Summary
Severity: Medium
Advisory: CVE-2018-0735
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-10-29
Source: https://osv.dev/vulnerability/CVE-2018-0735
Type: osv

## Details
The OpenSSL ECDSA signature algorithm has been shown to be vulnerable to a timing side channel attack. An attacker could use variations in the signing algorithm to recover the private key. Fixed in OpenSSL 1.1.0j (Affected 1.1.0-1.1.0i). Fixed in OpenSSL 1.1.1a (Affected 1.1.1).

## References
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=56fb454d281a023b3f950d969693553d3f3ceea1
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=b1d6d55ece1c26fa2829e2b819b038d7b6d692b4
- http://www.securityfocus.com/bid/105750
- http://www.securitytracker.com/id/1041986
- https://access.redhat.com/errata/RHSA-2019:3700
- https://lists.debian.org/debian-lts-announce/2018/11/msg00024.html
- https://nodejs.org/en/blog/vulnerability/november-2018-security-releases/
- https://security.netapp.com/advisory/ntap-20181105-0002/
- https://usn.ubuntu.com/3840-1/
- https://www.debian.org/security/2018/dsa-4348
- https://www.openssl.org/news/secadv/20181029.txt
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
