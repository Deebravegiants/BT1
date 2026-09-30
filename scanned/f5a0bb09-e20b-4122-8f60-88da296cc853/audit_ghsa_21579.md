# [M] Improper Certificate Validation in Liferay Portal

## Summary
Severity: Medium
Advisory: GHSA-cx84-43xc-3gm2
CVE: CVE-2022-42131
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-15
Source: https://github.com/advisories/GHSA-cx84-43xc-3gm2
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.1.0 <7.4.3.4

## Details
Certain Liferay products are affected by: Missing SSL Certificate Validation in the Dynamic Data Mapping module's REST data providers. This affects Liferay Portal 7.1.0 through 7.4.2 and Liferay DXP 7.1 before fix pack 27, 7.2 before fix pack 17, and 7.3 before service pack 3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42131
- https://issues.liferay.com/browse/LPE-17377
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-42131
- http://liferay.com
