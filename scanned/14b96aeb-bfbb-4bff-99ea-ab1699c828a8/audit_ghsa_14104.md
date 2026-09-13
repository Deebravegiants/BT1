# [M] Insecure Default Initialization In Liferay Portal

## Summary
Severity: Medium
Advisory: GHSA-g9mr-9xfc-4gf7
CVE: CVE-2023-33949
CWE: CWE-1188
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-24
Source: https://github.com/advisories/GHSA-g9mr-9xfc-4gf7
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.0.0 <7.3.1

## Details
In Liferay Portal 7.3.0 and earlier, and Liferay DXP 7.2 and earlier the default configuration does not require users to verify their email address, which allows remote attackers to create accounts using fake email addresses or email addresses which they don't control. The portal property `company.security.strangers.verify` should be set to true.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33949
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2023-33949
