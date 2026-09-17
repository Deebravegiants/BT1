# [M] CVE-2019-17451

## Summary
Severity: Medium
Advisory: CVE-2019-17451
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-10-10
Source: https://osv.dev/vulnerability/CVE-2019-17451
Type: osv

## Details
An issue was discovered in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.32. It is an integer overflow leading to a SEGV in _bfd_dwarf2_find_nearest_line in dwarf2.c, as demonstrated by nm.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=336bfbeb1848f4b9558456fdcf283ee8a32d7fd1
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00078.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00004.html
- https://security.gentoo.org/glsa/202007-39
- https://security.netapp.com/advisory/ntap-20191024-0002/
- https://usn.ubuntu.com/4336-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=25070
