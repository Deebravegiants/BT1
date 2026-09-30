# [M] CVE-2018-20673

## Summary
Severity: Medium
Advisory: CVE-2018-20673
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-04
Source: https://osv.dev/vulnerability/CVE-2018-20673
Type: osv

## Details
The demangle_template function in cplus-dem.c in GNU libiberty, as distributed in GNU Binutils 2.31.1, contains an integer overflow vulnerability (for "Create an array for saving the template argument values") that can trigger a heap-based buffer overflow, as demonstrated by nm.

## References
- http://www.securityfocus.com/bid/106454
- https://sourceware.org/bugzilla/show_bug.cgi?id=24039
