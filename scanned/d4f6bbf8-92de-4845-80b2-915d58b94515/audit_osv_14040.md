# [M] CVE-2018-6540

## Summary
Severity: Medium
Advisory: CVE-2018-6540
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-02
Source: https://osv.dev/vulnerability/CVE-2018-6540
Type: osv

## Details
In ZZIPlib 0.13.67, there is a bus error caused by loading of a misaligned address in the zzip_disk_findfirst function of zzip/mmapped.c. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted zip file.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00029.html
- https://usn.ubuntu.com/3699-1/
- https://github.com/gdraheim/zziplib/issues/15
