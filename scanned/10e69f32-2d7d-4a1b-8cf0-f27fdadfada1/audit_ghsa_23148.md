# [H] Liferay Portal and Liferay DXP have Insecure Deserialization Vulnerability

## Summary
Severity: High
Advisory: GHSA-mg3r-9jh8-33r9
CVE: CVE-2020-15842
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mg3r-9jh8-33r9
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.3.0
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.0.0 <7.0.10.fp90
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp17
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp5

## Details
Liferay Portal before 7.3.0, and Liferay DXP 7.0 before fix pack 90, 7.1 before fix pack 17, and 7.2 before fix pack 5, allows man-in-the-middle attackers to execute arbitrary code via crafted serialized payloads, because of insecure deserialization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15842
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-16963
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/119317427
