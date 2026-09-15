# [H] Missing authorization in Liferay portal

## Summary
Severity: High
Advisory: GHSA-w6f8-mxf5-4vf8
CVE: CVE-2023-33948
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-24
Source: https://github.com/advisories/GHSA-w6f8-mxf5-4vf8
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.3.67 <7.4.3.68

## Details
The Dynamic Data Mapping module in Liferay Portal 7.4.3.67, and Liferay DXP 7.4 update 67 does not limit Document and Media files which can be downloaded from a Form, which allows remote attackers to download any file from Document and Media via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33948
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2023-33948
