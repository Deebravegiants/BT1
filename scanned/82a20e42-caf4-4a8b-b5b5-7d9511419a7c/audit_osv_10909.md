# [M] CVE-2017-3735

## Summary
Severity: Medium
Advisory: CVE-2017-3735
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2017-08-28
Source: https://osv.dev/vulnerability/CVE-2017-3735
Type: osv

## Details
While parsing an IPAddressFamily extension in an X.509 certificate, it is possible to do a one-byte overread. This would result in an incorrect text display of the certificate. This bug has been present since 2006 and is present in all versions of OpenSSL before 1.0.2m and 1.1.0g.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://lists.debian.org/debian-lts-announce/2017/11/msg00011.html
- https://support.apple.com/HT208331
- https://usn.ubuntu.com/3611-2/
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.tenable.com/security/tns-2017-15
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- http://www.securityfocus.com/bid/100515
- http://www.securitytracker.com/id/1039726
- https://access.redhat.com/errata/RHSA-2018:3221
- https://access.redhat.com/errata/RHSA-2018:3505
- https://security.FreeBSD.org/advisories/FreeBSD-SA-17:11.openssl.asc
- https://security.gentoo.org/glsa/201712-03
- https://www.debian.org/security/2017/dsa-4017
- https://www.debian.org/security/2017/dsa-4018
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
