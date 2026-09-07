# [M] Unrestricted Upload of File with Dangerous Type in Liferay Portal and Liferay DXP

## Summary
Severity: Medium
Advisory: GHSA-c7f6-4vx5-4263
CVE: CVE-2020-15839
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-c7f6-4vx5-4263
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.1.10.fp18
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.1 <7.2.10.fp6

## Details
Liferay Portal before 7.3.3, and Liferay DXP 7.1 before fix pack 18 and 7.2 before fix pack 6, does not restrict the size of a multipart/form-data POST action, which allows remote authenticated users to conduct denial-of-service attacks by uploading large files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15839
- https://issues.liferay.com/browse/LPE-17029
- https://issues.liferay.com/browse/LPE-17055
- https://portal.liferay.dev/learn/security/known-vulnerabilities
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/119784928
