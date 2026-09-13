# [M] Liferay Portal and DXP allows users to add a note to a different virtual instance

## Summary
Severity: Medium
Advisory: GHSA-f372-9rcj-8w2c
CVE: CVE-2025-43810
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-23
Source: https://github.com/advisories/GHSA-f372-9rcj-8w2c
Type: github-advisory

## Affected
- Maven: `com.liferay.commerce:com.liferay.commerce.service` — affected >=0 <11.0.164

## Details
Insecure Direct Object Reference (IDOR) vulnerability with commerce order notes in Liferay Portal 7.3.5 through 7.4.3.112, and Liferay DXP 2023.Q4.0 through 2023.Q4.8, 2023.Q3.1 through 2023.Q3.10, and 7.4 GA through update 92 allows remote authenticated users to from one virtual instance to add a note to an order in a different virtual instance via the _com_liferay_commerce_order_web_internal_portlet_CommerceOrderPortlet_commerceOrderId parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43810
- https://github.com/liferay/liferay-portal/commit/72259fbf5a81596e99b615df480dee0b0fa3aa09
- https://github.com/liferay/liferay-portal/commit/9fad6a23b3c04146ef80a59b056f24b17cc2e721
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17935
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43810
