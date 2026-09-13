# [C] CVE-2017-14952

## Summary
Severity: Critical
Advisory: CVE-2017-14952
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-16
Source: https://osv.dev/vulnerability/CVE-2017-14952
Type: osv

## Details
Double free in i18n/zonemeta.cpp in International Components for Unicode (ICU) for C/C++ through 59.1 allows remote attackers to execute arbitrary code via a crafted string, aka a "redundant UVector entry clean up function call" issue.

## References
- http://www.sourcebrella.com/blog/double-free-vulnerability-international-components-unicode-icu/
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- http://bugs.icu-project.org/trac/changeset/40324/trunk/icu4c/source/i18n/zonemeta.cpp
