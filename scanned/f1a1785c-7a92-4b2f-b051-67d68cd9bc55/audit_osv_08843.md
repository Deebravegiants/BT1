# [C] CVE-2016-6309

## Summary
Severity: Critical
Advisory: CVE-2016-6309
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/CVE-2016-6309
Type: osv

## Details
statem/statem.c in OpenSSL 1.1.0a does not consider memory-block movement after a realloc call, which allows remote attackers to cause a denial of service (use-after-free) or possibly execute arbitrary code via a crafted TLS session.

## References
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://www-01.ibm.com/support/docview.wss?uid=swg21995039
- http://www.securityfocus.com/bid/93177
- http://www.securitytracker.com/id/1036885
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=acacbfa7565c78d2273c0b2a2e5e803f44afefeb
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03856en_us
- https://www.tenable.com/security/tns-2016-16
- https://www.tenable.com/security/tns-2016-20
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2017-3236622.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
- https://bto.bluecoat.com/security-advisory/sa132
- https://www.openssl.org/news/secadv/20160926.txt
