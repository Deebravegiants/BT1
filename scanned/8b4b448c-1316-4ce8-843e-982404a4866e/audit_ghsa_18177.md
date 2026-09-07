# [M] Liferay Portal vulnerable to cross-site scripting in the Calendar widget

## Summary
Severity: Medium
Advisory: GHSA-gj92-p9mh-83j8
CVE: CVE-2025-43818
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-30
Source: https://github.com/advisories/GHSA-gj92-p9mh-83j8
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.calendar.web` — affected >=5.0.45 <5.0.87

## Details
Cross-site scripting (XSS) vulnerability in the Calendar widget in Liferay Portal 7.4.3.35 through 7.4.3.110, and Liferay DXP 2023.Q4.0 through 2023.Q4.4, 2023.Q3.1 through 2023.Q3.6, 7.4 update 35 through update 92, and 7.3 update 25 through update 36 allows remote attackers to inject arbitrary web script or HTML via a crafted payload injected into a Calendar's “Name” text field

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43818
- https://github.com/liferay/liferay-portal/commit/ed066f19934a721a7f9b567db097e04cf4adbdae
- https://github.com/liferay/liferay-portal/commit/ff1d01a6bd2898e827b1efdf723ef24f7f2bb1bf
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17911
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43818
