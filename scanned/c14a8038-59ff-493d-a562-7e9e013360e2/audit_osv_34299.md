# [M] Dataease DB2 Aspectweaver Deserialization Arbitrary File Write Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-57773
Aliases: GHSA-7r8j-6whv-4j5p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-08-25
Source: https://osv.dev/vulnerability/CVE-2025-57773
Type: osv

## Details
DataEase is an open source business intelligence and data visualization tool. Prior to version 2.10.12, because DB2 parameters are not filtered, a JNDI injection attack can be directly launched. JNDI triggers an AspectJWeaver deserialization attack, writing to various files. This vulnerability requires commons-collections 4.x and aspectjweaver-1.9.22.jar. The vulnerability has been fixed in version 2.10.12.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57773.json
- https://github.com/dataease/dataease/security/advisories/GHSA-7r8j-6whv-4j5p
- https://nvd.nist.gov/vuln/detail/CVE-2025-57773
- https://github.com/dataease/dataease/commit/8d04e92d44e1bac9284e9e64df5afd7f96d9373c
