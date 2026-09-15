# [H] CVE-2019-20910

## Summary
Severity: High
Advisory: CVE-2019-20910
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2020-07-16
Source: https://osv.dev/vulnerability/CVE-2019-20910
Type: osv

## Details
An issue was discovered in GNU LibreDWG through 0.9.3. Crafted input will lead to a heap-based buffer over-read in decode_R13_R2000 in decode.c, a different vulnerability than CVE-2019-20011.

## References
- https://github.com/LibreDWG/libredwg/commit/f878ba67b638f0d5050b6dba61b9737f64fc53de
- https://github.com/LibreDWG/libredwg/issues/178
