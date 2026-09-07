# [M] Cross-site scripting in Liferay Portal

## Summary
Severity: Medium
Advisory: GHSA-53mw-69qx-q4fc
CVE: CVE-2023-33939
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-24
Source: https://github.com/advisories/GHSA-53mw-69qx-q4fc
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.1.0 <7.4.3.13

## Details
Cross-site scripting (XSS) vulnerability in the Modified Facet widget in Liferay Portal 7.1.0 through 7.4.3.12, and Liferay DXP 7.1 before fix pack 27, 7.2 before fix pack 18, 7.3 before update 4, and 7.4 before update 9 allows remote attackers to inject arbitrary web script or HTML via a crafted payload injected into a facet label.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33939
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2023-33939
