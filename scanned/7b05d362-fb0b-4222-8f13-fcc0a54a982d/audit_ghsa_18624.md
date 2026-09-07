# [M] Liferay Portal is vulnerable to XSS through its workflow process builder

## Summary
Severity: Medium
Advisory: GHSA-xcvw-hh99-qm73
CVE: CVE-2025-62239
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-xcvw-hh99-qm73
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.workflow.kaleo.designer.web` — affected >=5.0.56 <5.0.124

## Details
Cross-site scripting (XSS) vulnerability in workflow process builder in Liferay Portal 7.4.3.21 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.8, and 7.4 update 21 through update 92 allows remote authenticated attackers to inject arbitrary web script or HTML via the crafted input in a workflow definition.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62239
- https://github.com/liferay/liferay-portal/commit/3acad2d8683688ce022abf2dfbab9fb500c5a619
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17919
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62239
