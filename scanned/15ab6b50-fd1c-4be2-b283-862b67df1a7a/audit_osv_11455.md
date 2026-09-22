# [C] CVE-2017-7882

## Summary
Severity: Critical
Advisory: CVE-2017-7882
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-15
Source: https://osv.dev/vulnerability/CVE-2017-7882
Type: osv

## Details
LibreOffice before 2017-03-14 has an out-of-bounds write related to the HWPFile::TagsRead function in hwpfilter/source/hwpfile.cxx.

## References
- http://www.libreoffice.org/about-us/security/advisories/cve-2017-7882/
- http://www.securityfocus.com/bid/97684
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=860
- https://github.com/LibreOffice/core/commit/65dcd1d8195069c8c8acb3a188b8e5616c51029c
