# [M] CVE-2018-18484

## Summary
Severity: Medium
Advisory: CVE-2018-18484
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-18
Source: https://osv.dev/vulnerability/CVE-2018-18484
Type: osv

## Details
An issue was discovered in cp-demangle.c in GNU libiberty, as distributed in GNU Binutils 2.31. Stack Exhaustion occurs in the C++ demangling functions provided by libiberty, and there is a stack consumption problem caused by recursive stack frames: cplus_demangle_type, d_bare_function_type, d_function_type.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- https://usn.ubuntu.com/4326-1/
- https://usn.ubuntu.com/4336-1/
- http://www.securityfocus.com/bid/105693
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=87636
