# [H] CVE-2020-35980

## Summary
Severity: High
Advisory: CVE-2020-35980
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2020-35980
Type: osv

## Details
An issue was discovered in GPAC version 0.8.0 and 1.0.1. There is a use-after-free in the function gf_isom_box_del() in isomedia/box_funcs.c.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/commit/5aba27604d957e960d8069d85ccaf868f8a7b07a
- https://github.com/gpac/gpac/issues/1661
