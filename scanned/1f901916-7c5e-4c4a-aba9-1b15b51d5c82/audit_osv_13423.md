# [M] CVE-2018-19838

## Summary
Severity: Medium
Advisory: CVE-2018-19838
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-04
Source: https://osv.dev/vulnerability/CVE-2018-19838
Type: osv

## Details
In LibSass prior to 3.5.5, functions inside ast.cpp for IMPLEMENT_AST_OPERATORS expansion allow attackers to cause a denial-of-service resulting from stack consumption via a crafted sass file, as demonstrated by recursive calls involving clone(), cloneChildren(), and copy().

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00027.html
- https://github.com/sass/libsass/issues/2660
