# [C] CVE-2018-13005

## Summary
Severity: Critical
Advisory: CVE-2018-13005
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-29
Source: https://osv.dev/vulnerability/CVE-2018-13005
Type: osv

## Details
An issue was discovered in MP4Box in GPAC 0.7.1. The function urn_Read in isomedia/box_code_base.c has a heap-based buffer over-read.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00024.html
- https://usn.ubuntu.com/3926-1/
- https://github.com/gpac/gpac/issues/1088
