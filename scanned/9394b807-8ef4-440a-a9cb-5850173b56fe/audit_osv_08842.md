# [M] CVE-2016-6308

## Summary
Severity: Medium
Advisory: CVE-2016-6308
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/CVE-2016-6308
Type: osv

## Details
statem/statem_dtls.c in the DTLS implementation in OpenSSL 1.1.0 before 1.1.0a allocates memory before checking for an excessive length, which might allow remote attackers to cause a denial of service (memory consumption) via crafted DTLS messages.

## References
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://www-01.ibm.com/support/docview.wss?uid=swg21995039
- http://www.securityfocus.com/bid/93151
- http://www.securitytracker.com/id/1036885
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=df6b5e29ffea2d5a3e08de92fb765fdb21c7a21e
- https://www.tenable.com/security/tns-2016-16
- https://www.tenable.com/security/tns-2016-20
- https://www.tenable.com/security/tns-2016-21
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2017-3236622.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- https://bto.bluecoat.com/security-advisory/sa132
- https://www.openssl.org/news/secadv/20160922.txt
