# [M] CVE-2018-20407

## Summary
Severity: Medium
Advisory: CVE-2018-20407
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-23
Source: https://osv.dev/vulnerability/CVE-2018-20407
Type: osv

## Details
An issue was discovered in Bento4 1.5.1-627. There is a memory leak in AP4_DescriptorFactory::CreateDescriptorFromStream in Core/Ap4DescriptorFactory.cpp, as demonstrated by mp42hls.

## References
- https://github.com/axiomatic-systems/Bento4/issues/343
