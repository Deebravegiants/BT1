# [M] CVE-2019-8905

## Summary
Severity: Medium
Advisory: CVE-2019-8905
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2019-02-18
Source: https://osv.dev/vulnerability/CVE-2019-8905
Type: osv

## Details
do_core_note in readelf.c in libmagic.a in file 5.35 has a stack-based buffer over-read, related to file_printable, a different vulnerability than CVE-2018-10360.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00053.html
- http://www.securityfocus.com/bid/107137
- https://lists.debian.org/debian-lts-announce/2019/02/msg00044.html
- https://usn.ubuntu.com/3911-1/
- https://bugs.astron.com/view.php?id=63
