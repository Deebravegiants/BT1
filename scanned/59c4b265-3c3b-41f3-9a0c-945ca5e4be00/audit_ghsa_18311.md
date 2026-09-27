# [M] Liferay Portal is vulnerable to SSRF through custom object attachment fields

## Summary
Severity: Medium
Advisory: GHSA-477q-x55m-j38g
CVE: CVE-2025-43763
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-477q-x55m-j38g
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.object.service` — affected >=0 <1.0.208

## Details
A server-side request forgery (SSRF) vulnerability exist in the Liferay Portal  7.4.0 through 7.4.3.131, and Liferay DXP 2024.Q4.0 through 2024.Q4.7, 2024.Q3.0 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13 and 2024.Q1.1 through 2024.Q1.20 that affects custom object attachment fields. This flaw allows an attacker to manipulate the application into making unauthorized requests to other instances, creating new object entries that link to external resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43763
- https://github.com/liferay/liferay-portal/commit/0adf32842d055f40accc8b341c4feb11a9728261
- https://github.com/liferay/liferay-portal/commit/e5fe3f9e9916e66a896e7c321e641c6eabbf4dae
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18182
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43763
