# [H] CVE-2020-23928

## Summary
Severity: High
Advisory: CVE-2020-23928
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2020-23928
Type: osv

## Details
An issue was discovered in gpac before 1.0.1. The abst_box_read function in box_code_adobe.c has a heap-based buffer over-read.

## References
- https://github.com/gpac/gpac/issues/1568
- https://github.com/gpac/gpac/issues/1569
- https://github.com/gpac/gpac/commit/8e05648d6b4459facbc783025c5c42d301fef5c3
- https://cwe.mitre.org/data/definitions/126.html
