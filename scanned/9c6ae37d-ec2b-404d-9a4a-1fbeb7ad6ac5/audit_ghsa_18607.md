# [M] Liferay Portal is vulnerable to XSS through its Calendar Events parameters

## Summary
Severity: Medium
Advisory: GHSA-5264-m964-7pg9
CVE: CVE-2025-62240
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-09
Source: https://github.com/advisories/GHSA-5264-m964-7pg9
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.calendar.web` — affected >=5.0.45 <5.0.88

## Details
Multiple cross-site scripting (XSS) vulnerabilities with Calendar events in Liferay Portal 7.4.3.35 through 7.4.3.111, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.7, 7.4 update 35 through update 92, and 7.3 update 25 through update 36 allow remote attackers to inject arbitrary web script or HTML via a crafted payload injected into a user’s (1) First Name, (2) Middle Name or (3) Last Name text field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62240
- https://github.com/liferay/liferay-portal/commit/961b569fbd9207c728a93d962e989dbc062f6fb6
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62240
