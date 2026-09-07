# [M] Liferay Portal has Improper Validation of Specified Quantity in Input

## Summary
Severity: Medium
Advisory: GHSA-xvgg-9h29-4g34
CVE: CVE-2025-43793
CWE: CWE-1284
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-xvgg-9h29-4g34
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <96.0.0
- Maven: `com.liferay.portal:com.liferay.portal.kernel` — affected >=0 <130.0.1

## Details
Liferay Portal 7.4.0 through 7.4.3.105, and older unsupported versions, and Liferay DXP 2023.Q4.0, 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions may incorrectly identify the subdomain of a domain name and create a supercookie, which allows remote attackers who control a website that share the same TLD to read cookies set by the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43793
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43793
