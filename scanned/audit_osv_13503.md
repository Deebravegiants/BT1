# [M] CVE-2018-20095

## Summary
Severity: Medium
Advisory: CVE-2018-20095
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-12
Source: https://osv.dev/vulnerability/CVE-2018-20095
Type: osv

## Details
An issue was discovered in EnsureCapacity in Core/Ap4Array.h in Bento4 1.5.1-627. Crafted MP4 input triggers an attempt at excessive memory allocation, as demonstrated by mp42hls.

## References
- https://github.com/axiomatic-systems/Bento4/issues/341
