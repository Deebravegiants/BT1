# [M] CVE-2020-19488

## Summary
Severity: Medium
Advisory: CVE-2020-19488
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-07-21
Source: https://osv.dev/vulnerability/CVE-2020-19488
Type: osv

## Details
An issue was discovered in box_code_apple.c:119 in Gpac MP4Box 0.8.0, allows attackers to cause a Denial of Service due to an invalid read on function ilst_item_Read.

## References
- https://github.com/gpac/gpac/commit/6170024568f4dda310e98ef7508477b425c58d09
- https://github.com/gpac/gpac/issues/1263
