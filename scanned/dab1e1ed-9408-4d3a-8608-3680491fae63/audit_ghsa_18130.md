# [M] Liferay Portal Commerce component has Incorrect Permission Assignment for Critical Resource

## Summary
Severity: Medium
Advisory: GHSA-chr3-w547-85hw
CVE: CVE-2025-43808
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-19
Source: https://github.com/advisories/GHSA-chr3-w547-85hw
Type: github-advisory

## Affected
- Maven: `com.liferay.commerce:com.liferay.commerce.product.type.virtual.service` — affected >=0 <4.0.47

## Details
The Commerce component in Liferay Portal 7.3.0 through 7.4.3.112, and Liferay DXP 2023.Q4.0 through 2023.Q4.8, 2023.Q3.1 through 2023.Q3.10, 7.4 GA through update 92, and 7.3 Service Pack 3 through update 35 saves virtual products uploaded to Documents and Media with guest view permission, which allows remote attackers to access and download virtual products for free via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43808
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43808
