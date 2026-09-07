# [M] Liferay Portal is vulnerable to CSRF through publication comments

## Summary
Severity: Medium
Advisory: GHSA-9676-rh83-cr86
CVE: CVE-2025-62245
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-9676-rh83-cr86
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.change.tracking.web` — affected >=2.0.9 <2.0.121

## Details
Cross-site request forgery (CSRF) vulnerability in Liferay Portal 7.4.1 through 7.4.3.112, and Liferay DXP 2023.Q4.0 through 2023.Q4.5, 2023.Q3.1 through 2023.Q3.10, and 7.4 GA through update 92 allows remote attackers to add and edit publication comments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62245
- https://github.com/liferay/liferay-portal/commit/dd89fff675f04d146fda38a1bec884cf40d0c756
- https://github.com/liferay/liferay-portal/commit/fa356d07ab239e790b7e460d33c25184aef58716
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17932
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62245
