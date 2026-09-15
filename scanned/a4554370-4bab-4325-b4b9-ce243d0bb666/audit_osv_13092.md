# [M] CVE-2018-17359

## Summary
Severity: Medium
Advisory: CVE-2018-17359
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-23
Source: https://osv.dev/vulnerability/CVE-2018-17359
Type: osv

## Details
An issue was discovered in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.31. An invalid memory access exists in bfd_zalloc in opncls.c. Attackers could leverage this vulnerability to cause a denial of service (application crash) via a crafted ELF file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00072.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00008.html
- https://usn.ubuntu.com/4336-1/
- https://sourceware.org/bugzilla/show_bug.cgi?id=23686
