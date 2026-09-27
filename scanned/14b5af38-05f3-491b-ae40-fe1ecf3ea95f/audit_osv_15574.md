# [M] CVE-2019-17450

## Summary
Severity: Medium
Advisory: CVE-2019-17450
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-10-10
Source: https://osv.dev/vulnerability/CVE-2019-17450
Type: osv

## Details
find_abstract_instance in dwarf2.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.32, allows remote attackers to cause a denial of service (infinite recursion and application crash) via a crafted ELF file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00078.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00004.html
- https://security.gentoo.org/glsa/202007-39
- https://security.netapp.com/advisory/ntap-20191024-0002/
- https://usn.ubuntu.com/4336-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=25078
