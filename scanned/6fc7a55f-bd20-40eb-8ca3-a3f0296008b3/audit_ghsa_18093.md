# [M] Liferay Portal allows open redirect in /c/portal/edit_info_item parameter redirect

## Summary
Severity: Medium
Advisory: GHSA-6hj4-v2qp-cqr2
CVE: CVE-2025-43767
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-08-23
Source: https://github.com/advisories/GHSA-6hj4-v2qp-cqr2
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.info.impl` — affected >=0 <5.0.69

## Details
Open Redirect vulnerability in /c/portal/edit_info_item parameter redirect in Liferay Portal 7.4.3.86 through 7.4.3.131, and Liferay DXP 2024.Q3.1 through 2024.Q3.9, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.12 and 7.4 update 86 through update 92 allows an attacker to exploit this security vulnerability to redirect users to a malicious site.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43767
- https://github.com/liferay/liferay-portal/commit/04d6892c12f8c3d12085124b6cb856dfacb9bb89
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18139
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43767
