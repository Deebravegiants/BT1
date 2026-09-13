# [M] CVE-2018-20502

## Summary
Severity: Medium
Advisory: CVE-2018-20502
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-26
Source: https://osv.dev/vulnerability/CVE-2018-20502
Type: osv

## Details
An issue was discovered in Bento4 1.5.1-627. There is an attempt at excessive memory allocation in the AP4_DataBuffer class when called from AP4_HvccAtom::Create in Core/Ap4HvccAtom.cpp.

## References
- https://github.com/axiomatic-systems/Bento4/issues/349
