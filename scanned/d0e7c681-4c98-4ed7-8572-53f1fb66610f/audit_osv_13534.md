# [M] CVE-2018-20186

## Summary
Severity: Medium
Advisory: CVE-2018-20186
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-17
Source: https://osv.dev/vulnerability/CVE-2018-20186
Type: osv

## Details
An issue was discovered in Bento4 1.5.1-627. AP4_Sample::ReadData in Core/Ap4Sample.cpp allows attackers to trigger an attempted excessive memory allocation, related to AP4_DataBuffer::SetDataSize and AP4_DataBuffer::ReallocateBuffer in Core/Ap4DataBuffer.cpp.

## References
- https://github.com/axiomatic-systems/Bento4/issues/342
