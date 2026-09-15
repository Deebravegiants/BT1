# [H] CVE-2019-20915

## Summary
Severity: High
Advisory: CVE-2019-20915
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2020-07-16
Source: https://osv.dev/vulnerability/CVE-2019-20915
Type: osv

## Details
An issue was discovered in GNU LibreDWG through 0.9.3. Crafted input will lead to a heap-based buffer over-read in bit_write_TF in bits.c.

## References
- https://github.com/LibreDWG/libredwg/commit/95cc9300430d35feb05b06a9badf678419463dbe
- https://github.com/LibreDWG/libredwg/issues/178
