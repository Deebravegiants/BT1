# [M] CVE-2020-21913

## Summary
Severity: Medium
Advisory: CVE-2020-21913
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2020-21913
Type: osv

## Details
International Components for Unicode (ICU-20850) v66.1 was discovered to contain a use after free bug in the pkg_createWithAssemblyCode function in the file tools/pkgdata/pkgdata.cpp.

## References
- https://lists.debian.org/debian-lts-announce/2021/10/msg00008.html
- https://www.debian.org/security/2021/dsa-5014
- https://github.com/unicode-org/icu/pull/886
- https://unicode-org.atlassian.net/browse/ICU-20850
