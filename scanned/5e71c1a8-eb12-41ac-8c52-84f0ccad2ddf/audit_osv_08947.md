# [H] CVE-2016-7052

## Summary
Severity: High
Advisory: CVE-2016-7052
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/CVE-2016-7052
Type: osv

## Details
crypto/x509/x509_vfy.c in OpenSSL 1.0.2i allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) by triggering a CRL operation.

## References
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=6e629b5be45face20b4ca71c4fcbfed78b864a2e
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00013.html
- http://www-01.ibm.com/support/docview.wss?uid=swg21995039
- http://www.securityfocus.com/bid/93171
- http://www.securitytracker.com/id/1036885
- https://bto.bluecoat.com/security-advisory/sa132
- https://kc.mcafee.com/corporate/index?page=content&id=SB10171
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:27.openssl.asc
- https://security.gentoo.org/glsa/201612-16
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03856en_us
- https://www.openssl.org/news/secadv/20160926.txt
- https://www.tenable.com/security/tns-2016-16
- https://www.tenable.com/security/tns-2016-19
- https://www.tenable.com/security/tns-2016-20
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2017-3236622.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
