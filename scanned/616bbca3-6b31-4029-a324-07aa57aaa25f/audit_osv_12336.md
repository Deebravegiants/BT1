# [M] CVE-2018-11381

## Summary
Severity: Medium
Advisory: CVE-2018-11381
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11381
Type: osv

## Details
The string_scan_range() function in radare2 2.5.0 allows remote attackers to cause a denial of service (heap-based out-of-bounds read and application crash) via a crafted binary file.

## References
- https://github.com/radare/radare2/issues/9902
- https://github.com/radare/radare2/commit/3fcf41ed96ffa25b38029449520c8d0a198745f3
