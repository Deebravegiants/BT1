# [M] CVE-2017-6335

## Summary
Severity: Medium
Advisory: CVE-2017-6335
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-14
Source: https://osv.dev/vulnerability/CVE-2017-6335
Type: osv

## Details
The QuantumTransferMode function in coders/tiff.c in GraphicsMagick 1.3.25 and earlier allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a small samples per pixel value in a CMYKA TIFF file.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://usn.ubuntu.com/4206-1/
- http://www.securityfocus.com/bid/96544
- http://www.openwall.com/lists/oss-security/2017/02/28/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1427975
- https://sourceforge.net/p/graphicsmagick/code/ci/6156b4c2992d855ece6079653b3b93c3229fc4b8/
