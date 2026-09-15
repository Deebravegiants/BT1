# [M] Liferay Portal Does Not Limit Access to APIs Before Email Verification

## Summary
Severity: Medium
Advisory: GHSA-gv7w-jh8g-vr73
CVE: CVE-2025-62259
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-10-28
Source: https://github.com/advisories/GHSA-gv7w-jh8g-vr73
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1 <7.4.3.110

## Details
Liferay Portal 7.4.0 through 7.4.3.109, and older unsupported versions, and Liferay DXP 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions does not limit access to APIs before a user has verified their email address, which allows remote users to access and edit content via the API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62259
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62259
