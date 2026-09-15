# [M] CVE-2019-9072

## Summary
Severity: Medium
Advisory: CVE-2019-9072
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-24
Source: https://osv.dev/vulnerability/CVE-2019-9072
Type: osv

## Details
An issue was discovered in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.32. It is an attempted excessive memory allocation in setup_group in elf.c.

## References
- https://security.gentoo.org/glsa/202107-24
- https://support.f5.com/csp/article/K12541829
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=89396
- https://sourceware.org/bugzilla/show_bug.cgi?id=24232
- https://sourceware.org/bugzilla/show_bug.cgi?id=24237
- https://security.netapp.com/advisory/ntap-20190314-0003/
