# [M] CVE-2020-26519

## Summary
Severity: Medium
Advisory: CVE-2020-26519
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-10-02
Source: https://osv.dev/vulnerability/CVE-2020-26519
Type: osv

## Details
Artifex MuPDF before 1.18.0 has a heap based buffer over-write when parsing JBIG2 files allowing attackers to cause a denial of service.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Ba=commit%3Bh=af1e390a2c7abceb32676ec684cd1dbb92907ce8
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SOF4PX2A5TGKKPMXINADSOJJ4H5UUMKK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WJMBKWVY7ZBIQV3EU5YHEFH5XWV4PABG/
- https://lists.debian.org/debian-lts-announce/2021/03/msg00012.html
- https://security.gentoo.org/glsa/202105-30
- https://www.debian.org/security/2020/dsa-4794
- https://bugs.ghostscript.com/show_bug.cgi?id=702937
