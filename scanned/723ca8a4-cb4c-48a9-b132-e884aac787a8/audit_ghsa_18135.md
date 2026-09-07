# [M] Liferay Portal Uses Default Password

## Summary
Severity: Medium
Advisory: GHSA-43xf-59vr-g4f2
CVE: CVE-2025-43799
CWE: CWE-1393
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-43xf-59vr-g4f2
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0 <7.4.3.112

## Details
Liferay Portal 7.4.0 through 7.4.3.111, and older unsupported versions, and Liferay DXP 2023.Q4.0, 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92 and 7.3 GA through update 35, and older unsupported versions does not limit access to APIs before a user has changed their initial password, which allows remote users to access and edit content via the API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43799
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43799
