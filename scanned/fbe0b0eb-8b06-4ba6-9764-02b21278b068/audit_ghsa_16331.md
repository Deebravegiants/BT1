# [M] Privilege escalation in Liferay Portal

## Summary
Severity: Medium
Advisory: GHSA-mc8m-4r3w-q2hw
CVE: CVE-2022-45320
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-mc8m-4r3w-q2hw
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.4.3.16

## Details
Liferay Portal before 7.4.3.16 and Liferay DXP before 7.2 fix pack 19, 7.3 before update 6, and 7.4 before update 16 allow remote authenticated users to become the owner of a wiki page by editing the wiki page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45320
- https://github.com/liferay/liferay-portal
- https://github.com/liferay/liferay-portal/releases/tag/7.4.3.16-ga16
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2022-45320
