# [M] CVE-2018-20659

## Summary
Severity: Medium
Advisory: CVE-2018-20659
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-02
Source: https://osv.dev/vulnerability/CVE-2018-20659
Type: osv

## Details
An issue was discovered in Bento4 1.5.1-627. The AP4_StcoAtom class in Core/Ap4StcoAtom.cpp has an attempted excessive memory allocation when called from AP4_AtomFactory::CreateAtomFromStream in Core/Ap4AtomFactory.cpp, as demonstrated by mp42hls.

## References
- https://github.com/axiomatic-systems/Bento4/issues/350
