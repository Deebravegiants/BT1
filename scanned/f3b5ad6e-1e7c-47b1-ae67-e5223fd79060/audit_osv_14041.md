# [M] CVE-2018-6541

## Summary
Severity: Medium
Advisory: CVE-2018-6541
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-02
Source: https://osv.dev/vulnerability/CVE-2018-6541
Type: osv

## Details
In ZZIPlib 0.13.67, there is a bus error caused by loading of a misaligned address (when handling disk64_trailer local entries) in __zzip_fetch_disk_trailer (zzip/zip.c). Remote attackers could leverage this vulnerability to cause a denial of service via a crafted zip file.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00029.html
- https://access.redhat.com/errata/RHSA-2019:2196
- https://usn.ubuntu.com/3699-1/
- https://github.com/gdraheim/zziplib/issues/16
