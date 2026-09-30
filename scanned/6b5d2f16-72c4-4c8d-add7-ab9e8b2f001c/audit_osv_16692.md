# [H] CVE-2019-9070

## Summary
Severity: High
Advisory: CVE-2019-9070
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-24
Source: https://osv.dev/vulnerability/CVE-2019-9070
Type: osv

## Details
An issue was discovered in GNU libiberty, as distributed in GNU Binutils 2.32. It is a heap-based buffer over-read in d_expression_1 in cp-demangle.c after many recursive calls.

## References
- http://www.securityfocus.com/bid/107147
- https://security.gentoo.org/glsa/202107-24
- https://support.f5.com/csp/article/K13534168
- https://usn.ubuntu.com/4326-1/
- https://usn.ubuntu.com/4336-1/
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=89395
- https://sourceware.org/bugzilla/show_bug.cgi?id=24229
- https://security.netapp.com/advisory/ntap-20190314-0003/
