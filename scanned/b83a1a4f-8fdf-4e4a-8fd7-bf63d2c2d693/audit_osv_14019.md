# [M] CVE-2018-6381

## Summary
Severity: Medium
Advisory: CVE-2018-6381
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-29
Source: https://osv.dev/vulnerability/CVE-2018-6381
Type: osv

## Details
In ZZIPlib 0.13.67, 0.13.66, 0.13.65, 0.13.64, 0.13.63, 0.13.62, 0.13.61, 0.13.60, 0.13.59, 0.13.58, 0.13.57 and 0.13.56 there is a segmentation fault caused by invalid memory access in the zzip_disk_fread function (zzip/mmapped.c) because the size variable is not validated against the amount of file->stored data.

## References
- https://github.com/Hack-Me/Pocs_for_Multi_Versions/tree/main/CVE-2018-6381
- https://lists.debian.org/debian-lts-announce/2020/06/msg00029.html
- https://usn.ubuntu.com/3699-1/
- https://github.com/gdraheim/zziplib/issues/12
