# [M] CVE-2017-7607

## Summary
Severity: Medium
Advisory: CVE-2017-7607
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/CVE-2017-7607
Type: osv

## Details
The handle_gnu_hash function in readelf.c in elfutils 0.168 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted ELF file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00052.html
- http://www.securityfocus.com/bid/98608
- https://usn.ubuntu.com/3670-1/
- https://security.gentoo.org/glsa/201710-10
- https://blogs.gentoo.org/ago/2017/04/03/elfutils-heap-based-buffer-overflow-in-handle_gnu_hash-readelf-c
