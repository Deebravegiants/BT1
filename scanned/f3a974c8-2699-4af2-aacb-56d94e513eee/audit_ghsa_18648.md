# [M] Liferay Portal and DXP affected by multiple cross-site scripting (XSS) vulnerabilities in web content template’s select structure page

## Summary
Severity: Medium
Advisory: GHSA-q285-wfpg-93hr
CVE: CVE-2025-62267
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-31
Source: https://github.com/advisories/GHSA-q285-wfpg-93hr
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.dynamic.data.mapping.item.selector.web` — affected >=0 <1.0.9

## Details
Multiple cross-site scripting (XSS) vulnerabilities in web content template’s select structure page in Liferay Portal 7.4.3.35 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.10, 2023.Q3.1 through 2023.Q3.10, 7.4 update 35 through update 92 allow remote attackers to inject arbitrary web script or HTML via a crafted payload injected into a user’s (1) First Name, (2) Middle Name, or (3) Last Name text field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62267
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17900
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62267
