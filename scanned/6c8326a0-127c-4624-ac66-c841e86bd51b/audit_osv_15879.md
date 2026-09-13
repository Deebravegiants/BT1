# [M] CVE-2019-20171

## Summary
Severity: Medium
Advisory: CVE-2019-20171
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-31
Source: https://osv.dev/vulnerability/CVE-2019-20171
Type: osv

## Details
An issue was discovered in GPAC version 0.5.2 and 0.9.0-development-20191109. There are memory leaks in metx_New in isomedia/box_code_base.c and abst_Read in isomedia/box_code_adobe.c.

## References
- https://github.com/gpac/gpac/blob/v0.5.2/src/isomedia/box_code_adobe.c
- https://lists.debian.org/debian-lts-announce/2020/01/msg00017.html
- https://github.com/gpac/gpac/issues/1337
