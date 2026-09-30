# [M] CVE-2019-7698

## Summary
Severity: Medium
Advisory: CVE-2019-7698
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-10
Source: https://osv.dev/vulnerability/CVE-2019-7698
Type: osv

## Details
An issue was discovered in AP4_Array<AP4_CttsTableEntry>::EnsureCapacity in Core/Ap4Array.h in Bento4 1.5.1-627. Crafted MP4 input triggers an attempt at excessive memory allocation, as demonstrated by mp42hls, a related issue to CVE-2018-20095.

## References
- https://github.com/axiomatic-systems/Bento4/issues/354
