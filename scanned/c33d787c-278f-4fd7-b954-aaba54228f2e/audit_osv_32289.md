# [M] DataEase has an improper authentication vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-27138
Aliases: GHSA-533g-whf8-q637
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-13
Source: https://osv.dev/vulnerability/CVE-2025-27138
Type: osv

## Details
DataEase is an open source business intelligence and data visualization tool. Prior to version 2.10.6, there is a flaw in the authentication in the io.dataease.auth.filter.TokenFilter class, which may cause the risk of unauthorized access. The vulnerability has been fixed in v2.10.6. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27138.json
- https://github.com/dataease/dataease/security/advisories/GHSA-533g-whf8-q637
- https://nvd.nist.gov/vuln/detail/CVE-2025-27138
