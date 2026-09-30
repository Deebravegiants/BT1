# [M] CVE-2017-13775

## Summary
Severity: Medium
Advisory: CVE-2017-13775
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2017-13775
Type: osv

## Details
GraphicsMagick 1.3.26 has a denial of service issue in ReadJNXImage() in coders/jnx.c whereby large amounts of CPU and memory resources may be consumed although the file itself does not support the requests.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PF62B5PJA2JDUOCKJGUQO3SPL74BEYSV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WHIKB4TP6KBJWT2UIPWL5MWMG5QXKGEJ/
- https://usn.ubuntu.com/4222-1/
- https://www.debian.org/security/2018/dsa-4321
- http://www.securityfocus.com/bid/100570
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- http://hg.code.sf.net/p/graphicsmagick/code/rev/b037d79b6ccd
- http://openwall.com/lists/oss-security/2017/08/31/3
