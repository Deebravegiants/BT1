# [H] CVE-2017-16358

## Summary
Severity: High
Advisory: CVE-2017-16358
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-01
Source: https://osv.dev/vulnerability/CVE-2017-16358
Type: osv

## Details
In radare 2.0.1, an out-of-bounds read vulnerability exists in string_scan_range() in libr/bin/bin.c when doing a string search.

## References
- https://github.com/radare/radare2/commit/d31c4d3cbdbe01ea3ded16a584de94149ecd31d9
- https://github.com/radare/radare2/issues/8748
