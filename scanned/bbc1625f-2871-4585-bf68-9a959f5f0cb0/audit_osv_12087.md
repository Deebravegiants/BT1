# [H] CVE-2018-10120

## Summary
Severity: High
Advisory: CVE-2018-10120
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-16
Source: https://osv.dev/vulnerability/CVE-2018-10120
Type: osv

## Details
The SwCTBWrapper::Read function in sw/source/filter/ww8/ww8toolbar.cxx in LibreOffice before 5.4.6.1 and 6.x before 6.0.2.1 does not validate a customizations index, which allows remote attackers to cause a denial of service (heap-based buffer overflow with write access) or possibly have unspecified other impact via a crafted document that contains a certain Microsoft Word record.

## References
- https://gerrit.libreoffice.org/gitweb?p=core.git%3Ba=commit%3Bh=017fcc2fcd00af17a97bd5463d89662404f57667
- https://access.redhat.com/errata/RHSA-2018:3054
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=6173
- https://lists.debian.org/debian-lts-announce/2018/04/msg00021.html
- https://usn.ubuntu.com/3883-1/
- https://www.debian.org/security/2018/dsa-4178
- https://www.libreoffice.org/about-us/security/advisories/cve-2018-10120/
- https://gerrit.libreoffice.org/#/c/49486/
- https://gerrit.libreoffice.org/#/c/49499/
- https://gerrit.libreoffice.org/#/c/49500/
