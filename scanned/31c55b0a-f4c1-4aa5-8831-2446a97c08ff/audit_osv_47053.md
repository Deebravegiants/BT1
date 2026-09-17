# [M] CVE-2015-8808

## Summary
Severity: Medium
Advisory: CVE-2015-8808
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-07-13
Source: https://osv.dev/vulnerability/CVE-2015-8808
Type: osv

## Details
The DecodeImage function in coders/gif.c in GraphicsMagick 1.3.18 allows remote attackers to cause a denial of service (uninitialized memory access) via a crafted GIF file.

## References
- http://www.debian.org/security/2016/dsa-3746
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/177834.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00032.html
- http://marc.info/?l=graphicsmagick-commit&m=142283721604323&w=2
- http://www.openwall.com/lists/oss-security/2016/02/06/1
- http://www.openwall.com/lists/oss-security/2016/02/06/3
- http://www.securityfocus.com/bid/83058
