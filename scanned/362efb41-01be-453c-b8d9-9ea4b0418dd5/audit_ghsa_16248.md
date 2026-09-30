# [M] Liferay Portal and Liferay DXP Allows Authenticated Users with View Permissions to Edit Permissions

## Summary
Severity: Medium
Advisory: GHSA-pw7p-3648-qqmg
CVE: CVE-2024-25604
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-pw7p-3648-qqmg
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.2.0 <7.4.3.5-ga5
- Maven: `com.liferay.portal:release.dxp.bom` — affected 7.4.13
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.2.10.fp17

## Details
Liferay Portal 7.2.0 through 7.4.3.4, and older unsupported versions, and Liferay DXP 7.4.13, 7.3 before service pack 3, 7.2 before fix pack 17, and older unsupported versions does not properly check user permissions, which allows remote authenticated users with the VIEW user permission to edit their own permission via the User and Organizations section of the Control Panel.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25604
- https://github.com/liferay/liferay-portal/commit/4a196df20e180be76944cd0c623df486379d7724
- https://github.com/liferay/liferay-portal/commit/f028316fa975d2e13bed7ef49d69ab77f412765e
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2024-25604
