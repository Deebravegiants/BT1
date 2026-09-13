# [M] Liferay Portal fails to verify messages from the cluster network is trusted

## Summary
Severity: Medium
Advisory: GHSA-6pgj-w687-9c8c
CVE: CVE-2025-62250
CWE: CWE-346
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-21
Source: https://github.com/advisories/GHSA-6pgj-w687-9c8c
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.cluster.multiple` — affected >=0 <5.0.35

## Details
Improper Authentication in Liferay Portal 7.4.0 through 7.4.3.132, and older unsupported versions, and Liferay DXP 2023.Q4.0, 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions allows remote attackers to send malicious data to the Liferay Portal 7.4.0 through 7.4.3.132, and older unsupported versions, and Liferay DXP 2023.Q4.0, 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions that will treat it as trusted data via unauthenticated cluster messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62250
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17901
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62250
