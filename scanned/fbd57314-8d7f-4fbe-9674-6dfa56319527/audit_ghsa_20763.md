# [M] Liferay Portal Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-83qx-288m-72w4
CVE: CVE-2022-39975
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-09-23
Source: https://github.com/advisories/GHSA-83qx-288m-72w4
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.3.3 <7.4.3.35

## Details
The Layout module in Liferay Portal v7.3.3 through v7.4.3.34, and Liferay DXP 7.3 before update 10, and 7.4 before update 35 does not check user permission before showing the preview of a "Content Page" type page, allowing attackers to view unpublished "Content Page" pages via URL manipulation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-39975
- https://github.com/liferay/liferay-portal
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-39975
- http://liferay.com
