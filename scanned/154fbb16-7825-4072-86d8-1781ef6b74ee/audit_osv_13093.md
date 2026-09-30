# [M] CVE-2018-17360

## Summary
Severity: Medium
Advisory: CVE-2018-17360
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-23
Source: https://osv.dev/vulnerability/CVE-2018-17360
Type: osv

## Details
An issue was discovered in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.31. a heap-based buffer over-read in bfd_getl32 in libbfd.c allows an attacker to cause a denial of service through a crafted PE file. This vulnerability can be triggered by the executable objdump.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- https://usn.ubuntu.com/4336-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=23685
