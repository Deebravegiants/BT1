# [M] CVE-2019-9071

## Summary
Severity: Medium
Advisory: CVE-2019-9071
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-24
Source: https://osv.dev/vulnerability/CVE-2019-9071
Type: osv

## Details
An issue was discovered in GNU libiberty, as distributed in GNU Binutils 2.32. It is a stack consumption issue in d_count_templates_scopes in cp-demangle.c after many recursive calls.

## References
- http://www.securityfocus.com/bid/107147
- https://security.gentoo.org/glsa/202107-24
- https://support.f5.com/csp/article/K02884135
- https://usn.ubuntu.com/4326-1/
- https://usn.ubuntu.com/4336-1/
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=89394
- https://sourceware.org/bugzilla/show_bug.cgi?id=24227
- https://security.netapp.com/advisory/ntap-20190314-0003/
