# [M] CVE-2019-6966

## Summary
Severity: Medium
Advisory: CVE-2019-6966
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-25
Source: https://osv.dev/vulnerability/CVE-2019-6966
Type: osv

## Details
An issue was discovered in Bento4 1.5.1-628. The AP4_ElstAtom class in Core/Ap4ElstAtom.cpp has an attempted excessive memory allocation related to AP4_Array<AP4_ElstEntry>::EnsureCapacity in Core/Ap4Array.h, as demonstrated by mp42hls.

## References
- https://github.com/axiomatic-systems/Bento4/issues/361
