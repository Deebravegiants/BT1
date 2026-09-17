# [M] CVE-2017-16353

## Summary
Severity: Medium
Advisory: CVE-2017-16353
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-11-01
Source: https://osv.dev/vulnerability/CVE-2017-16353
Type: osv

## Details
GraphicsMagick 1.3.26 is vulnerable to a memory information disclosure vulnerability found in the DescribeImage function of the magick/describe.c file, because of a heap-based buffer over-read. The portion of the code containing the vulnerability is responsible for printing the IPTC Profile information contained in the image. This vulnerability can be triggered with a specially crafted MIFF file. There is an out-of-bounds buffer dereference because certain increments are never checked.

## References
- http://hg.graphicsmagick.org/hg/GraphicsMagick?cmd=changeset%3Bnode=e4e1c2a581d8
- https://usn.ubuntu.com/4232-1/
- http://www.securityfocus.com/bid/101653
- https://www.debian.org/security/2018/dsa-4321
- ftp://ftp.graphicsmagick.org/pub/GraphicsMagick/snapshots/ChangeLog.txt
- https://lists.debian.org/debian-lts-announce/2017/11/msg00002.html
- https://lists.debian.org/debian-lts-announce/2018/06/msg00009.html
- https://blogs.securiteam.com/index.php/archives/3494
- https://www.exploit-db.com/exploits/43111/
