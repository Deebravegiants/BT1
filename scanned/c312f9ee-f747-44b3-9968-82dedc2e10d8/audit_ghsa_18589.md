# [M] Liferay Portal Stores Password Reset Tokens in Plain Text

## Summary
Severity: Medium
Advisory: GHSA-xcj6-xpjg-c4xr
CVE: CVE-2025-62261
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-28
Source: https://github.com/advisories/GHSA-xcj6-xpjg-c4xr
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.0-ga1 <7.4.3.100
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <92.0.2

## Details
Liferay Portal 7.4.0 through 7.4.3.99, and older unsupported versions, and Liferay DXP 2023.Q3.1 through 2023.Q3.4, 7.4 GA through update 92, 7.3 GA through update 34, and older unsupported versions stores password reset tokens in plain text, which allows attackers with access to the database to obtain the token, reset a user’s password and take over the user’s account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62261
- https://github.com/liferay/liferay-portal/commit/b228c7878f2ed5ad8dbc1ff7ec9b5e6d53bb4b5c
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17785
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62261
