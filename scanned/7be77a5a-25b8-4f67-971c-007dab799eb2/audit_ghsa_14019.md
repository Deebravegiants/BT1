# [M] Liferay portal unauthorized access to objects via OAuth 2 scope

## Summary
Severity: Medium
Advisory: GHSA-2868-ff44-43qv
CVE: CVE-2023-33946
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-05-24
Source: https://github.com/advisories/GHSA-2868-ff44-43qv
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.3.4 <7.4.3.49

## Details
The Object module in Liferay Portal 7.4.3.4 through 7.4.3.48, and Liferay DXP 7.4 before update 49 does properly isolate objects in difference virtual instances, which allows remote authenticated users in one virtual instance to view objects in a different virtual instance via OAuth 2 scope administration page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33946
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2023-33946
