# [M] Liferay Portal Notifications Widget has multiple XSS vulnerabilities through various text fields

## Summary
Severity: Medium
Advisory: GHSA-q8fj-76q7-4p7h
CVE: CVE-2025-43771
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-q8fj-76q7-4p7h
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.flags.web` — affected >=6.0.23 <6.0.24

## Details
Multiple cross-site scripting (XSS) vulnerabilities in the Notifications widget in Liferay Portal 7.4.3.102 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.5 and 2023.Q3.1 through 2023.Q3.10 allow remote attackers to inject arbitrary web script or HTML via a crafted payload injected into (1) a user’s “First Name” text field, (2) a user’s “Middle Name” text field, (3) a user’s “Last Name” text field, (4) the “Other Reason” text field when flagging content, or (5) the name of the flagged content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43771
- https://github.com/liferay/liferay-portal/commit/0f1f6b628d40c9fc59ad6f561f6bdcc1208b5dbb
- https://github.com/liferay/liferay-portal/commit/28dc724658e13acb80f30fb3211d0849592ec4ef
- https://github.com/liferay/liferay-portal/commit/90b677d7ca74464f2079266588a67fa56aca842d
- https://github.com/liferay/liferay-portal/commit/cca5fe50a5b63000c3ca7469b668af9399025e90
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17917
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43771
