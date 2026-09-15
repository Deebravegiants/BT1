# [C] CVE-2017-7856

## Summary
Severity: Critical
Advisory: CVE-2017-7856
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2017-7856
Type: osv

## Details
LibreOffice before 2017-03-11 has an out-of-bounds write caused by a heap-based buffer overflow in the SVMConverter::ImplConvertFromSVM1 function in vcl/source/gdi/svmconverter.cxx.

## References
- http://www.libreoffice.org/about-us/security/advisories/cve-2017-7856/
- http://www.securityfocus.com/bid/97667
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=817
- https://github.com/LibreOffice/core/commit/28e61b634353110445e334ccaa415d7fb6629d62
