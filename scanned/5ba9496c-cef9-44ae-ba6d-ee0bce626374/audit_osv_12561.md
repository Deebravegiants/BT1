# [H] CVE-2018-12913

## Summary
Severity: High
Advisory: CVE-2018-12913
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-27
Source: https://osv.dev/vulnerability/CVE-2018-12913
Type: osv

## Details
In Miniz 2.0.7, tinfl_decompress in miniz_tinfl.c has an infinite loop because sym2 and counter can both remain equal to zero.

## References
- https://github.com/richgel999/miniz/issues/90
