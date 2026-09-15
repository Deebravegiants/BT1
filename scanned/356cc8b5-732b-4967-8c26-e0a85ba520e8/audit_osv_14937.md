# [M] CVE-2019-12481

## Summary
Severity: Medium
Advisory: CVE-2019-12481
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-05-30
Source: https://osv.dev/vulnerability/CVE-2019-12481
Type: osv

## Details
An issue was discovered in GPAC 0.7.1. There is a NULL pointer dereference in the function GetESD at isomedia/track.c in libgpac.a, as demonstrated by MP4Box.

## References
- https://lists.debian.org/debian-lts-announce/2019/06/msg00030.html
- https://github.com/gpac/gpac/issues/1249
