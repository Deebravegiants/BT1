# [M] CVE-2016-9888

## Summary
Severity: Medium
Advisory: CVE-2016-9888
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-12-08
Source: https://osv.dev/vulnerability/CVE-2016-9888
Type: osv

## Details
An error within the "tar_directory_for_file()" function (gsf-infile-tar.c) in GNOME Structured File Library before 1.14.41 can be exploited to trigger a Null pointer dereference and subsequently cause a crash via a crafted TAR file.

## References
- http://www.securityfocus.com/bid/94860
- https://lists.debian.org/debian-lts-announce/2020/04/msg00016.html
- https://secunia.com/advisories/71201/
- https://secunia.com/secunia_research/2016-17/
- https://github.com/GNOME/libgsf/commit/95a8351a75758cf10b3bf6abae0b6b461f90d9e5
