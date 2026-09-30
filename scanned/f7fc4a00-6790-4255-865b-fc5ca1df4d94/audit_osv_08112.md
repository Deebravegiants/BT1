# [C] CVE-2016-10327

## Summary
Severity: Critical
Advisory: CVE-2016-10327
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2016-10327
Type: osv

## Details
LibreOffice before 2016-12-22 has an out-of-bounds write caused by a heap-based buffer overflow related to the EnhWMFReader::ReadEnhWMF function in vcl/source/filter/wmf/enhwmf.cxx.

## References
- http://www.libreoffice.org/about-us/security/advisories/cve-2016-10327/
- http://www.securityfocus.com/bid/97668
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=313
- https://security.gentoo.org/glsa/201706-28
- https://github.com/LibreOffice/core/commit/7485fc2a1484f31631f62f97e5c64c0ae74c6416
