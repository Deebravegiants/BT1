# [H] Liferay Portal is vulnerable to Insecure Direct Object Reference (IDOR) attack through Authentication Bypass

## Summary
Severity: High
Advisory: GHSA-5wxc-3jfw-w94p
CVE: CVE-2025-43790
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-11
Source: https://github.com/advisories/GHSA-5wxc-3jfw-w94p
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.object.service` — affected >=0 <1.0.197

## Details
An Insecure Direct Object Reference (IDOR) vulnerability in Liferay Portal 7.4.0 through 7.4.3.124, and Liferay DXP 2024.Q2.0 through 2024.Q2.6, 2024.Q1.1 through 2024.Q1.12 and 7.4 GA through update 92 allows remote authenticated users to from one virtual instance to access, create, edit, relate data/object entries/definitions to an object in a different virtual instance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43790
- https://github.com/liferay/liferay-portal/commit/66b9a7dc4d40a10dec03e169ca8735add81e9bd9
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18065
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43790
