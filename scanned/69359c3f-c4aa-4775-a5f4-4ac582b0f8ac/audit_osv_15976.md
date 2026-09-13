# [H] CVE-2019-20913

## Summary
Severity: High
Advisory: CVE-2019-20913
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2020-07-16
Source: https://osv.dev/vulnerability/CVE-2019-20913
Type: osv

## Details
An issue was discovered in GNU LibreDWG through 0.9.3. Crafted input will lead to a heap-based buffer over-read in dwg_encode_entity in common_entity_data.spec.

## References
- https://github.com/LibreDWG/libredwg/commit/3f503dd294efc63a59608d8a16058c41d44ba13a
- https://github.com/LibreDWG/libredwg/issues/178
