# [M] CVE-2019-20911

## Summary
Severity: Medium
Advisory: CVE-2019-20911
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-07-16
Source: https://osv.dev/vulnerability/CVE-2019-20911
Type: osv

## Details
An issue was discovered in GNU LibreDWG through 0.9.3. Crafted input will lead to denial of service in bit_calc_CRC in bits.c, related to a for loop.

## References
- https://github.com/LibreDWG/libredwg/commit/c6f6668b82bfe595899cc820279ac37bb9ef16f5
- https://github.com/LibreDWG/libredwg/issues/178
