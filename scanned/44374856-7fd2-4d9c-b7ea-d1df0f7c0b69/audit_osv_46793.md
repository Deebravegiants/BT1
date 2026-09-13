# [M] CVE-2015-3197

## Summary
Severity: Medium
Advisory: CVE-2015-3197
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-02-15
Source: https://osv.dev/vulnerability/CVE-2015-3197
Type: osv

## Details
ssl/s2_srvr.c in OpenSSL 1.0.1 before 1.0.1r and 1.0.2 before 1.0.2f does not prevent use of disabled ciphers, which makes it easier for man-in-the-middle attackers to defeat cryptographic protection mechanisms by performing computations on SSLv2 traffic, related to the get_client_master_key and get_client_hello functions.

## References
- http://www.openssl.org/news/secadv/20160128.txt
- http://www.oracle.com/technetwork/security-advisory/cpujul2016-2881720.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2017-3236622.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:11.openssl.asc
- https://security.gentoo.org/glsa/201601-05
- http://www.oracle.com/technetwork/security-advisory/cpuapr2016v3-2985753.html
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/176373.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00012.html
