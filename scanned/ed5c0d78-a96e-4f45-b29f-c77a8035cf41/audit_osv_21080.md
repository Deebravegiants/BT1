# [M] CVE-2021-40491

## Summary
Severity: Medium
Advisory: CVE-2021-40491
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-09-03
Source: https://osv.dev/vulnerability/CVE-2021-40491
Type: osv

## Details
The ftp client in GNU Inetutils before 2.2 does not validate addresses returned by PASV/LSPV responses to make sure they match the server address. This is similar to CVE-2020-8284 for curl.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=993476
- https://lists.debian.org/debian-lts-announce/2022/11/msg00033.html
- https://lists.gnu.org/archive/html/bug-inetutils/2021-06/msg00002.html
- https://git.savannah.gnu.org/cgit/inetutils.git/commit/?id=58cb043b190fd04effdaea7c9403416b436e50dd
