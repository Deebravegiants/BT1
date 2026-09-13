# [M] Liferay Portal and DXP vulnerable to a memory leak

## Summary
Severity: Medium
Advisory: GHSA-hrqm-qpw9-w8rv
CVE: CVE-2025-43816
CWE: CWE-401
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-25
Source: https://github.com/advisories/GHSA-hrqm-qpw9-w8rv
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.vulcan.impl` — affected >=0 <5.0.115

## Details
A memory leak in the headless API for StructuredContents in Liferay Portal 7.4.0 through 7.4.3.119, and older unsupported versions, and Liferay DXP 2024.Q1.1 through 2024.Q1.5, 2023.Q4.0 through 2024.Q4.10, 2023.Q3.1 through 2023.Q3.10, 7.4 GA through update 92, and older unsupported versions allows an attacker to cause server unavailability (denial of service) via repeatedly calling the API endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43816
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18005
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43816
