# [M] CVE-2019-9073

## Summary
Severity: Medium
Advisory: CVE-2019-9073
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-24
Source: https://osv.dev/vulnerability/CVE-2019-9073
Type: osv

## Details
An issue was discovered in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.32. It is an attempted excessive memory allocation in _bfd_elf_slurp_version_tables in elf.c.

## References
- https://security.gentoo.org/glsa/202107-24
- https://support.f5.com/csp/article/K37121474
- https://usn.ubuntu.com/4336-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=24233
- https://security.netapp.com/advisory/ntap-20190314-0003/
