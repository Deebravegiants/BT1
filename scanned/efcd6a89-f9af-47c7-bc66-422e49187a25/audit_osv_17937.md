# [M] CVE-2020-21839

## Summary
Severity: Medium
Advisory: CVE-2020-21839
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-05-17
Source: https://osv.dev/vulnerability/CVE-2020-21839
Type: osv

## Details
An issue was discovered in GNU LibreDWG 0.10. Crafted input will lead to an memory leak in dwg_decode_eed ../../src/decode.c:3638.

## References
- https://github.com/LibreDWG/libredwg/issues/188#issuecomment-574492707
- https://cwe.mitre.org/data/definitions/401.html
