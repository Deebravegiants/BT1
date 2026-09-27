# [M] CVE-2019-14250

## Summary
Severity: Medium
Advisory: CVE-2019-14250
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-24
Source: https://osv.dev/vulnerability/CVE-2019-14250
Type: osv

## Details
An issue was discovered in GNU libiberty, as distributed in GNU Binutils 2.32. simple_object_elf_match in simple-object-elf.c does not check for a zero shstrndx value, leading to an integer overflow and resultant heap-based buffer overflow.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00057.html
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00058.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00078.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00004.html
- http://www.securityfocus.com/bid/109354
- https://security.gentoo.org/glsa/202007-39
- https://security.netapp.com/advisory/ntap-20190822-0002/
- https://usn.ubuntu.com/4326-1/
- https://usn.ubuntu.com/4336-1/
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=90924
- https://gcc.gnu.org/ml/gcc-patches/2019-07/msg01003.html
