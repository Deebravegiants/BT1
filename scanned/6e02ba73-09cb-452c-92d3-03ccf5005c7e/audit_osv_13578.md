# [M] CVE-2018-20409

## Summary
Severity: Medium
Advisory: CVE-2018-20409
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-23
Source: https://osv.dev/vulnerability/CVE-2018-20409
Type: osv

## Details
An issue was discovered in Bento4 1.5.1-627. There is a heap-based buffer over-read in AP4_AvccAtom::Create in Core/Ap4AvccAtom.cpp, as demonstrated by mp42hls.

## References
- https://github.com/axiomatic-systems/Bento4/issues/345
