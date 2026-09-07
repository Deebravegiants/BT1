# [M] Liferay Portal Vulnerable to Open Redirect via the _com_liferay_layout_admin_web_portlet_GroupPagesPortlet_redirect parameter

## Summary
Severity: Medium
Advisory: GHSA-2pwh-9q9q-5r9c
CVE: CVE-2025-62253
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-10-27
Source: https://github.com/advisories/GHSA-2pwh-9q9q-5r9c
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.layout.admin.web` — affected >=5.0.8 <5.0.157

## Details
Open redirect vulnerability in page administration in Liferay Portal 7.4.0 through 7.4.3.97, and older unsupported versions, and Liferay DXP 2023.Q4.0, 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions allows remote attackers to redirect users to arbitrary external URLs via the _com_liferay_layout_admin_web_portlet_GroupPagesPortlet_redirect parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62253
- https://github.com/liferay/liferay-portal/commit/2835554ffe37ac4ba3b794e6d6c0bfd1dc8db301
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17838
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62253
