# [M] CVE-2017-13776

## Summary
Severity: Medium
Advisory: CVE-2017-13776
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2017-13776
Type: osv

## Details
GraphicsMagick 1.3.26 has a denial of service issue in ReadXBMImage() in a coders/xbm.c "Read hex image data" version!=10 case that results in the reader not returning; it would cause large amounts of CPU and memory consumption although the crafted file itself does not request it.

## References
- https://usn.ubuntu.com/4222-1/
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://www.debian.org/security/2018/dsa-4321
- http://www.securityfocus.com/bid/100574
- http://hg.code.sf.net/p/graphicsmagick/code/rev/233a720bfd5e
- http://openwall.com/lists/oss-security/2017/08/31/2
