# [M] CVE-2018-17985

## Summary
Severity: Medium
Advisory: CVE-2018-17985
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-04
Source: https://osv.dev/vulnerability/CVE-2018-17985
Type: osv

## Details
An issue was discovered in cp-demangle.c in GNU libiberty, as distributed in GNU Binutils 2.31. There is a stack consumption problem caused by the cplus_demangle_type function making recursive calls to itself in certain scenarios involving many 'P' characters.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- https://usn.ubuntu.com/4326-1/
- https://usn.ubuntu.com/4336-1/
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=87335
