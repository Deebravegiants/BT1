# [H] CVE-2020-23931

## Summary
Severity: High
Advisory: CVE-2020-23931
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2020-23931
Type: osv

## Details
An issue was discovered in gpac before 1.0.1. The abst_box_read function in box_code_adobe.c has a heap-based buffer over-read.

## References
- https://cwe.mitre.org/data/definitions/126.html
- https://github.com/gpac/gpac/issues/1564
- https://github.com/gpac/gpac/issues/1567
- https://github.com/gpac/gpac/commit/093283e727f396130651280609e687cd4778e0d1
