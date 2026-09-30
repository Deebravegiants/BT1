# [H] CVE-2016-6305

## Summary
Severity: High
Advisory: CVE-2016-6305
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/CVE-2016-6305
Type: osv

## Details
The ssl3_read_bytes function in record/rec_layer_s3.c in OpenSSL 1.1.0 before 1.1.0a allows remote attackers to cause a denial of service (infinite loop) by triggering a zero-length record in an SSL_peek call.

## References
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://www-01.ibm.com/support/docview.wss?uid=swg21995039
- http://www.securityfocus.com/bid/93149
- http://www.securitytracker.com/id/1036879
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=63658103d4441924f8dbfc517b99bb54758a98b9
- https://www.tenable.com/security/tns-2016-16
- https://www.tenable.com/security/tns-2016-20
- https://www.tenable.com/security/tns-2016-21
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2017-3236622.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- https://bto.bluecoat.com/security-advisory/sa132
- https://security.gentoo.org/glsa/201612-16
- https://www.openssl.org/news/secadv/20160922.txt
- https://github.com/openssl/openssl/issues/1563
