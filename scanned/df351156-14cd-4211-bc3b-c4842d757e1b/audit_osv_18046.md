# [M] CVE-2020-23269

## Summary
Severity: Medium
Advisory: CVE-2020-23269
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-22
Source: https://osv.dev/vulnerability/CVE-2020-23269
Type: osv

## Details
An issue was discovered in gpac 0.8.0. The stbl_GetSampleSize function in isomedia/stbl_read.c has a heap-based buffer overflow which can lead to a denial of service (DOS) via a crafted media file.

## References
- https://github.com/gpac/gpac/issues/1482
