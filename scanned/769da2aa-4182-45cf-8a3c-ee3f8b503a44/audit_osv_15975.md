# [H] CVE-2019-20912

## Summary
Severity: High
Advisory: CVE-2019-20912
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-07-16
Source: https://osv.dev/vulnerability/CVE-2019-20912
Type: osv

## Details
An issue was discovered in GNU LibreDWG through 0.9.3. Crafted input will lead to a stack overflow in bits.c, possibly related to bit_read_TF.

## References
- https://github.com/LibreDWG/libredwg/commit/b84c2cab55948a5ee70860779b2640913e3ee1ed
- https://github.com/LibreDWG/libredwg/issues/178
