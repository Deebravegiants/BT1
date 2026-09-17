# [H] CVE-2017-16352

## Summary
Severity: High
Advisory: CVE-2017-16352
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-01
Source: https://osv.dev/vulnerability/CVE-2017-16352
Type: osv

## Details
GraphicsMagick 1.3.26 is vulnerable to a heap-based buffer overflow vulnerability found in the "Display visual image directory" feature of the DescribeImage() function of the magick/describe.c file. One possible way to trigger the vulnerability is to run the identify command on a specially crafted MIFF format file with the verbose flag.

## References
- http://hg.graphicsmagick.org/hg/GraphicsMagick?cmd=changeset%3Bnode=7292230dd185
- https://usn.ubuntu.com/4232-1/
- ftp://ftp.graphicsmagick.org/pub/GraphicsMagick/snapshots/ChangeLog.txt
- https://lists.debian.org/debian-lts-announce/2017/11/msg00002.html
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://www.debian.org/security/2018/dsa-4321
- http://www.securityfocus.com/bid/101658
- https://www.exploit-db.com/exploits/43111/
- https://blogs.securiteam.com/index.php/archives/3494
