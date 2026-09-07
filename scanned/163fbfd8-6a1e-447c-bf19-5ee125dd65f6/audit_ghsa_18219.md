# [M] Liferay Portal vulnerable to reflected cross-site scripting on the page configuration page

## Summary
Severity: Medium
Advisory: GHSA-wmjx-xv9v-r89q
CVE: CVE-2025-43815
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-30
Source: https://github.com/advisories/GHSA-wmjx-xv9v-r89q
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.product.navigation.control.menu.web` — affected >=6.0.80 <6.0.83

## Details
Reflected cross-site scripting (XSS) vulnerability on the page configuration page in Liferay Portal 7.4.3.102 through 7.4.3.110, and Liferay DXP 2023.Q4.0 through 2023.Q4.2, and 2023.Q3.5 allows remote attackers to inject arbitrary web script or HTML via the com_liferay_layout_admin_web_portlet_GroupPagesPortlet_backURLTitle parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43815
- https://github.com/liferay/liferay-portal/commit/30d07ef9c95c66828818a4ba577ff56f8e2dd0d3
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17903
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43815
