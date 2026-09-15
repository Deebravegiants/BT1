# [M] CVE-2018-20712

## Summary
Severity: Medium
Advisory: CVE-2018-20712
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-15
Source: https://osv.dev/vulnerability/CVE-2018-20712
Type: osv

## Details
A heap-based buffer over-read exists in the function d_expression_1 in cp-demangle.c in GNU libiberty, as distributed in GNU Binutils 2.31.1. A crafted input can cause segmentation faults, leading to denial-of-service, as demonstrated by c++filt.

## References
- http://www.securityfocus.com/bid/106563
- https://support.f5.com/csp/article/K38336243
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=88629
- https://sourceware.org/bugzilla/show_bug.cgi?id=24043
