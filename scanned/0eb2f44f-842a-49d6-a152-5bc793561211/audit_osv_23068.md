# [M] CVE-2022-43032

## Summary
Severity: Medium
Advisory: CVE-2022-43032
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-10-19
Source: https://osv.dev/vulnerability/CVE-2022-43032
Type: osv

## Details
An issue was discovered in Bento4 v1.6.0-639. There is a memory leak in AP4_DescriptorFactory::CreateDescriptorFromStream in Core/Ap4DescriptorFactory.cpp, as demonstrated by mp42aac.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43032.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43032
- https://github.com/axiomatic-systems/Bento4/issues/763
