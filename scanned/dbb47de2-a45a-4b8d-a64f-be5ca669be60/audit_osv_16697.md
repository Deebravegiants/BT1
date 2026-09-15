# [H] CVE-2019-9075

## Summary
Severity: High
Advisory: CVE-2019-9075
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-24
Source: https://osv.dev/vulnerability/CVE-2019-9075
Type: osv

## Details
An issue was discovered in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.32. It is a heap-based buffer overflow in _bfd_archive_64_bit_slurp_armap in archive64.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00078.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00004.html
- https://security.gentoo.org/glsa/202107-24
- https://support.f5.com/csp/article/K42059040
- https://usn.ubuntu.com/4336-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=24236
- https://security.netapp.com/advisory/ntap-20190314-0003/
