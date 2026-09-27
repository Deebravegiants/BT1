# [M] CVE-2018-0739

## Summary
Severity: Medium
Advisory: CVE-2018-0739
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-27
Source: https://osv.dev/vulnerability/CVE-2018-0739
Type: osv

## Details
Constructed ASN.1 types with a recursive definition (such as can be found in PKCS7) could eventually exceed the stack given malicious input with excessive recursion. This could result in a Denial Of Service attack. There are no such structures used within SSL/TLS that come from untrusted sources so this is considered safe. Fixed in OpenSSL 1.1.0h (Affected 1.1.0-1.1.0g). Fixed in OpenSSL 1.0.2o (Affected 1.0.2b-1.0.2n).

## References
- http://www.securityfocus.com/bid/105609
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=2ac4c6f7b2b2af20c0e2b0ba05367e454cd11b33
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=9310d45087ae546e27e61ddf8f6367f29848220d
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.tenable.com/security/tns-2018-04
- https://www.tenable.com/security/tns-2018-06
- https://www.tenable.com/security/tns-2018-07
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- http://www.securityfocus.com/bid/103518
- http://www.securitytracker.com/id/1040576
- https://access.redhat.com/errata/RHSA-2018:3090
- https://access.redhat.com/errata/RHSA-2018:3221
- https://access.redhat.com/errata/RHSA-2018:3505
- https://access.redhat.com/errata/RHSA-2019:0366
- https://access.redhat.com/errata/RHSA-2019:0367
- https://access.redhat.com/errata/RHSA-2019:1711
- https://access.redhat.com/errata/RHSA-2019:1712
- https://lists.debian.org/debian-lts-announce/2018/03/msg00033.html
- https://security.gentoo.org/glsa/201811-21
