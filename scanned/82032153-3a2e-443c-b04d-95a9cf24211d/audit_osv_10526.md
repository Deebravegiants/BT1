# [H] CVE-2017-16832

## Summary
Severity: High
Advisory: CVE-2017-16832
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-15
Source: https://osv.dev/vulnerability/CVE-2017-16832
Type: osv

## Details
The pe_bfd_read_buildid function in peicode.h in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.29.1, does not validate size and offset values in the data dictionary, which allows remote attackers to cause a denial of service (segmentation violation and application crash) or possibly have unspecified other impact via a crafted PE file.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git%3Bh=0bb6961f18b8e832d88b490d421ca56cea16c45b
- https://security.gentoo.org/glsa/201811-17
- https://sourceware.org/bugzilla/show_bug.cgi?id=22373
