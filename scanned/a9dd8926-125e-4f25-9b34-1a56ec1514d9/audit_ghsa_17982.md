# [M] Liferay Portal vulnerable to Reflected XSS with the referer and forward parameter

## Summary
Severity: Medium
Advisory: GHSA-h4m4-xp33-37mj
CVE: CVE-2025-43770
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-08-23
Source: https://github.com/advisories/GHSA-h4m4-xp33-37mj
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.kernel` — affected >=0 <155.0.0

## Details
A reflected cross-site scripting (XSS) vulnerability in the Liferay Portal 7.4.0 through 7.4.3.131, and Liferay DXP 2024.Q4.0 through 2024.Q4.3, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.12 and 7.4 GA through update 92  allows an remote non-authenticated attacker to inject JavaScript into the referer or FORWARD_URL using %00 in those parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-43770
- https://github.com/liferay/liferay-portal/commit/a712758b9c4b6f4c54df5dec7d334279bb30f75a
- https://github.com/liferay/liferay-portal/commit/bf20bc07e3e3421d39eaacff052418ce26d791f2
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-18151
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-43770
