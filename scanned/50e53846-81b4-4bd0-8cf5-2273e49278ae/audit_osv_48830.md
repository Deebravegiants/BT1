# [H] CVE-2018-14912

## Summary
Severity: High
Advisory: CVE-2018-14912
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-03
Source: https://osv.dev/vulnerability/CVE-2018-14912
Type: osv

## Details
cgit_clone_objects in CGit before 1.2.1 has a directory traversal vulnerability when `enable-http-clone=1` is not turned off, as demonstrated by a cgit/cgit.cgi/git/objects/?path=../ request.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00005.html
- https://lists.zx2c4.com/pipermail/cgit/2018-August/004176.html
- https://www.debian.org/security/2018/dsa-4263
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1627
- https://www.exploit-db.com/exploits/45195/
