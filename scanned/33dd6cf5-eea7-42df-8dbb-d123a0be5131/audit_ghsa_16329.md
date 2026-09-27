# [M] Liferay Portal's account lockout does not invalidate existing user sessions

## Summary
Severity: Medium
Advisory: GHSA-2mx7-xvfg-fg53
CVE: CVE-2023-47798
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-08
Source: https://github.com/advisories/GHSA-2mx7-xvfg-fg53
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.2.0 <7.3.1
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp5

## Details
Account lockout in Liferay Portal 7.2.0 through 7.3.0, and older unsupported versions, and Liferay DXP 7.2 before fix pack 5, and older unsupported versions does not invalidate existing user sessions, which allows remote authenticated users to remain authenticated after an account has been locked.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47798
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2023-47798
