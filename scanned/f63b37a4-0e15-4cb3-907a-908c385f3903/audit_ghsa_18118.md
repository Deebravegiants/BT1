# [M] Liferay Portal allows remote attackers to view display page templates via crafted URLs

## Summary
Severity: Medium
Advisory: GHSA-5pp7-m8x8-rc82
CVE: CVE-2025-43805
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-5pp7-m8x8-rc82
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.asset.display.page.service` — affected >=0 <4.0.55

## Details
Liferay Portal 7.3.0 through 7.4.3.111, and Liferay DXP 2023.Q4.0, 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, and 7.3 GA through update 35 does not perform an authorization check when users attempt to view a display page template, which allows remote attackers to view display page templates via crafted URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43805
- https://github.com/liferay/liferay-portal/compare/7.4.3.111-ga111...7.4.3.112-ga112
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43805
