# [M] CVE-2018-5388

## Summary
Severity: Medium
Advisory: CVE-2018-5388
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-31
Source: https://osv.dev/vulnerability/CVE-2018-5388
Type: osv

## Details
In stroke_socket.c in strongSwan before 5.6.3, a missing packet length check could allow a buffer underflow, which may lead to resource exhaustion and denial of service while reading from the socket.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00077.html
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00047.html
- http://packetstormsecurity.com/files/172833/strongSwan-VPN-Charon-Server-Buffer-Overflow.html
- https://git.strongswan.org/?p=strongswan.git%3Ba=commitdiff%3Bh=0acd1ab4
- http://www.kb.cert.org/vuls/id/338343
- http://www.securityfocus.com/bid/104263
- https://security.gentoo.org/glsa/201811-16
- https://usn.ubuntu.com/3771-1/
- https://www.debian.org/security/2018/dsa-4229
