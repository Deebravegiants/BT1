# [H] CVE-2018-10119

## Summary
Severity: High
Advisory: CVE-2018-10119
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-16
Source: https://osv.dev/vulnerability/CVE-2018-10119
Type: osv

## Details
sot/source/sdstor/stgstrms.cxx in LibreOffice before 5.4.5.1 and 6.x before 6.0.1.1 uses an incorrect integer data type in the StgSmallStrm class, which allows remote attackers to cause a denial of service (use-after-free with write access) or possibly have unspecified other impact via a crafted document that uses the structured storage ole2 wrapper file format.

## References
- https://gerrit.libreoffice.org/gitweb?p=core.git%3Ba=commit%3Bh=fdd41c995d1f719e92c6f083e780226114762f05
- https://access.redhat.com/errata/RHSA-2018:3054
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=5747
- https://lists.debian.org/debian-lts-announce/2018/04/msg00021.html
- https://usn.ubuntu.com/3883-1/
- https://www.debian.org/security/2018/dsa-4178
- https://www.libreoffice.org/about-us/security/advisories/cve-2018-10119/
- https://gerrit.libreoffice.org/#/c/48751/
- https://gerrit.libreoffice.org/#/c/48756/
- https://gerrit.libreoffice.org/#/c/48757/
- https://gerrit.libreoffice.org/#/c/48758/
