# [M] CVE-2018-11377

## Summary
Severity: Medium
Advisory: CVE-2018-11377
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11377
Type: osv

## Details
The avr_op_analyze() function in radare2 2.5.0 allows remote attackers to cause a denial of service (heap-based out-of-bounds read and application crash) via a crafted binary file.

## References
- https://github.com/radare/radare2/issues/9901
- https://github.com/radare/radare2/commit/25a3703ef2e015bbe1d1f16f6b2f63bb10dd34f4
- https://github.com/radare/radare2/commit/b35530fa0681b27eba084de5527037ebfb397422
