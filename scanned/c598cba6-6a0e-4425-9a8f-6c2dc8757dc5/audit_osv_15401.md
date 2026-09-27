# [H] CVE-2019-15847

## Summary
Severity: High
Advisory: CVE-2019-15847
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-02
Source: https://osv.dev/vulnerability/CVE-2019-15847
Type: osv

## Details
The POWER9 backend in GNU Compiler Collection (GCC) before version 10 could optimize multiple calls of the __builtin_darn intrinsic into a single call, thus reducing the entropy of the random number generator. This occurred because a volatile operation was not specified. For example, within a single execution of a program, the output of every __builtin_darn() call may be the same.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00057.html
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00058.html
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=91481
