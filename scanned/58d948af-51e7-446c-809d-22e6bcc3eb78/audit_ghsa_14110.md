# [M] Liferay portal has unauthorized access to object definition via search 

## Summary
Severity: Medium
Advisory: GHSA-769c-p92r-xgxj
CVE: CVE-2023-33947
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-05-24
Source: https://github.com/advisories/GHSA-769c-p92r-xgxj
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.3.4 <7.4.3.61

## Details
The Object module in Liferay Portal 7.4.3.4 through 7.4.3.60, and Liferay DXP 7.4 before update 61 does not segment object definition by virtual instance in search which allows remote authenticated users in one virtual instance to view object definition from a second virtual instance by searching for the object definition.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33947
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2023-33947
