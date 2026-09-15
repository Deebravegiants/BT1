# [H] CVE-2020-35982

## Summary
Severity: High
Advisory: CVE-2020-35982
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2020-35982
Type: osv

## Details
An issue was discovered in GPAC version 0.8.0 and 1.0.1. There is an invalid pointer dereference in the function gf_hinter_track_finalize() in media_tools/isom_hinter.c.

## References
- https://github.com/gpac/gpac/commit/a4eb327049132359cae54b59faec9e2f14c5a619
- https://github.com/gpac/gpac/issues/1660
