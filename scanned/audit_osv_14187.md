# [M] CVE-2018-7726

## Summary
Severity: Medium
Advisory: CVE-2018-7726
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-06
Source: https://osv.dev/vulnerability/CVE-2018-7726
Type: osv

## Details
An issue was discovered in ZZIPlib 0.13.68. There is a bus error caused by the __zzip_parse_root_directory function of zip.c. Attackers could leverage this vulnerability to cause a denial of service via a crafted zip file.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00029.html
- https://access.redhat.com/errata/RHSA-2018:3229
- https://usn.ubuntu.com/3699-1/
- https://github.com/gdraheim/zziplib/issues/41
