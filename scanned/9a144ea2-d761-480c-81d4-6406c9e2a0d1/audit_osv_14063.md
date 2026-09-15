# [M] CVE-2018-6869

## Summary
Severity: Medium
Advisory: CVE-2018-6869
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2018-6869
Type: osv

## Details
In ZZIPlib 0.13.68, there is an uncontrolled memory allocation and a crash in the __zzip_parse_root_directory function of zzip/zip.c. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted zip file.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00029.html
- http://www.securityfocus.com/bid/103050
- https://usn.ubuntu.com/3699-1/
- https://lists.debian.org/debian-lts-announce/2018/02/msg00022.html
- https://github.com/gdraheim/zziplib/issues/22
