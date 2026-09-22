# [M] CVE-2018-6484

## Summary
Severity: Medium
Advisory: CVE-2018-6484
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-01
Source: https://osv.dev/vulnerability/CVE-2018-6484
Type: osv

## Details
In ZZIPlib 0.13.67, there is a memory alignment error and bus error in the __zzip_fetch_disk_trailer function of zzip/zip.c. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted zip file.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00029.html
- https://usn.ubuntu.com/3699-1/
- https://github.com/gdraheim/zziplib/issues/14
