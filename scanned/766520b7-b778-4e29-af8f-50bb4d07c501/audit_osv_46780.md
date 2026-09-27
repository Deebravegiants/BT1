# [M] CVE-2015-2326

## Summary
Severity: Medium
Advisory: CVE-2015-2326
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-01-14
Source: https://osv.dev/vulnerability/CVE-2015-2326
Type: osv

## Details
The pcre_compile2 function in PCRE before 8.37 allows context-dependent attackers to compile incorrect code and cause a denial of service (out-of-bounds read) via regular expression with a group containing both a forward referencing subroutine call and a recursive back reference, as demonstrated by "((?+1)(\1))/".

## References
- http://lists.opensuse.org/opensuse-updates/2015-05/msg00014.html
- https://bugs.exim.org/show_bug.cgi?id=1592
- https://fortiguard.com/zeroday/FG-VD-15-016
- https://www.pcre.org/original/changelog.txt
- http://lists.opensuse.org/opensuse-updates/2015-05/msg00014.html
- https://bugs.exim.org/show_bug.cgi?id=1592
- https://bugs.exim.org/show_bug.cgi?id=1592
