# [M] Liferay Commerce Order Content Web is Vulnerable to Authorization Bypass Through User-Controlled Key

## Summary
Severity: Medium
Advisory: GHSA-fhcw-px4q-pmvv
CVE: CVE-2025-62241
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-13
Source: https://github.com/advisories/GHSA-fhcw-px4q-pmvv
Type: github-advisory

## Affected
- Maven: `com.liferay.commerce:com.liferay.commerce.order.content.web` — affected >=0 <4.0.114

## Details
Insecure Direct Object Reference (IDOR) vulnerability with shipment addresses in Liferay DXP 2023.Q4.1 through 2023.Q4.5 allows remote authenticated users to from one virtual instance to view the shipment addresses of different virtual instance via the _com_liferay_commerce_order_web_internal_portlet_CommerceOrderPortlet_commerceOrderId parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62241
- https://github.com/liferay/liferay-portal/commit/53401963f02f593bbf555b4b321fdaeb59e03a53
- https://github.com/liferay/liferay-portal/commit/75c39ea518eb91b3b5cbb0576074ebbbfd805401
- https://liferay.atlassian.net/browse/LPE-17936
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62241
