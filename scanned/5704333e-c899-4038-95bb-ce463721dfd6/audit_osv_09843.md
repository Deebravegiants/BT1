# [M] CVE-2017-11671

## Summary
Severity: Medium
Advisory: CVE-2017-11671
CVSS: 4.0 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-11671
Type: osv

## Details
Under certain circumstances, the ix86_expand_builtin function in i386.c in GNU Compiler Collection (GCC) version 4.6, 4.7, 4.8, 4.9, 5 before 5.5, and 6 before 6.4 will generate instruction sequences that clobber the status flag of the RDRAND and RDSEED intrinsics before it can be read, potentially causing failures of these instructions to go unreported. This could potentially lead to less randomness in random number generation.

## References
- http://openwall.com/lists/oss-security/2017/07/27/2
- http://www.securityfocus.com/bid/100018
- https://access.redhat.com/errata/RHSA-2018:0849
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=80180
- https://gcc.gnu.org/ml/gcc-patches/2017-03/msg01349.html
