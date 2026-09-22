# [C] CVE-2017-7870

## Summary
Severity: Critical
Advisory: CVE-2017-7870
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2017-7870
Type: osv

## Details
LibreOffice before 2017-01-02 has an out-of-bounds write caused by a heap-based buffer overflow related to the tools::Polygon::Insert function in tools/source/generic/poly.cxx.

## References
- http://www.securitytracker.com/id/1039029
- http://www.debian.org/security/2017/dsa-3837
- http://www.libreoffice.org/about-us/security/advisories/cve-2017-7870/
- http://www.securityfocus.com/bid/97671
- https://access.redhat.com/errata/RHSA-2017:1975
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=372
- https://security.gentoo.org/glsa/201706-28
- https://github.com/LibreOffice/core/commit/62a97e6a561ce65e88d4c537a1b82c336f012722
