# [H] CVE-2017-14120

## Summary
Severity: High
Advisory: CVE-2017-14120
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-03
Source: https://osv.dev/vulnerability/CVE-2017-14120
Type: osv

## Details
unrar 0.0.1 (aka unrar-free or unrar-gpl) suffers from a directory traversal vulnerability for RAR v2 archives: pathnames of the form ../[filename] are unpacked into the upper directory.

## References
- http://www.openwall.com/lists/oss-security/2017/08/20/1
- https://lists.debian.org/debian-lts-announce/2021/02/msg00026.html
- https://bugs.debian.org/874059
