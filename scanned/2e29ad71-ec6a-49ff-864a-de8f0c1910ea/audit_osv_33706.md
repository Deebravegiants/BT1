# [H] Dataease MYSQL JDBC File Reading Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-48998
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-06-03
Source: https://osv.dev/vulnerability/CVE-2025-48998
Type: osv

## Details
DataEase is an open source business intelligence and data visualization tool. Prior to version 2.10.6, a bypass of the patch for CVE-2025-27103 allows authenticated users to read and deserialize arbitrary files through the background JDBC connection. The vulnerability has been fixed in v2.10.10. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48998.json
- https://github.com/dataease/dataease/security/advisories/GHSA-2wfc-qwx7-w692
- https://github.com/dataease/dataease/security/advisories/GHSA-v4gg-8rp3-ccjx
- https://nvd.nist.gov/vuln/detail/CVE-2025-48998
