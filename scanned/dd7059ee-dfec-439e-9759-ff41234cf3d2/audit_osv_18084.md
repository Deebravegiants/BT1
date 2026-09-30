# [M] CVE-2020-23861

## Summary
Severity: Medium
Advisory: CVE-2020-23861
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-05-18
Source: https://osv.dev/vulnerability/CVE-2020-23861
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in LibreDWG 0.10.1 via the read_system_page function at libredwg-0.10.1/src/decode_r2007.c:666:5, which causes a denial of service by submitting a dwg file.

## References
- https://github.com/LibreDWG/libredwg/issues/248
