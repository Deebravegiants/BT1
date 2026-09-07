# [M] Liferay Portal is vulnerable to XSS attack through fieldset name in Kaleo Forms Admin

## Summary
Severity: Medium
Advisory: GHSA-cpg4-qcj8-42gp
CVE: CVE-2025-43778
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-cpg4-qcj8-42gp
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.portal.workflow.kaleo.forms.web` — affected >=5.0.3 <5.0.107

## Details
A Stored cross-site scripting vulnerability in the Liferay Portal  7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q2.0 through 2025.Q2.11, 2025.Q1.0 through 2025.Q1.16, 2024.Q4.0 through 2024.Q4.7, 2024.Q3.0 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13 and 2024.Q1.1 through 2024.Q1.20 allows an remote authenticated attacker to inject JavaScript through the name of a fieldset in Kaleo Forms Admin. The malicious payload is stored and executed without proper sanitization or escaping.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43778
- https://github.com/liferay/liferay-portal/commit/a540e050d0d939218cfb90b1e5b6c21244a834cb
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43778
