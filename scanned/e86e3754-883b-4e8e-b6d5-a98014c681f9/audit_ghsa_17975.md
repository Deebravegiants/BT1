# [M] Liferay Portal ReDoS with Role Name search in KaleoDesignerPortlet

## Summary
Severity: Medium
Advisory: GHSA-23w4-rpc6-wpcc
CVE: CVE-2025-43764
CWE: CWE-1333
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:L/VI:L/VA:H/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-08-23
Source: https://github.com/advisories/GHSA-23w4-rpc6-wpcc
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.workflow.kaleo.designer.web` — affected >=0 <5.0.145

## Details
Self-ReDoS (Regular expression Denial of Service) exists with Role Name search field of Kaleo Designer portlet JavaScript in Liferay Portal 7.4.0 through 7.4.3.131, and Liferay DXP 2024.Q4.0 through 2024.Q4.1, 2024.Q3.0 through 2024.Q3.13, 2024.Q2.1 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.20 and 7.4 GA through update 92, which allows authenticated users with permissions to update Kaleo Workflows to enter a malicious Regex pattern causing their browser to hang for a very long time.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43764
- https://github.com/liferay/liferay-portal/commit/12a076172494707748325836b3d5236507be0490
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18148
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43764
