# [M] Authorization Bypass in Liferay Portal

## Summary
Severity: Medium
Advisory: GHSA-g6x4-57hp-j4xm
CVE: CVE-2022-42129
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-11-15
Source: https://github.com/advisories/GHSA-g6x4-57hp-j4xm
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.3.2 <7.4.3.5

## Details
An Insecure direct object reference (IDOR) vulnerability in the Dynamic Data Mapping module in Liferay Portal 7.3.2 through 7.4.3.4, and Liferay DXP 7.3 before update 4, and 7.4 GA allows remote authenticated users to view and access form entries via the `formInstanceRecordId` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42129
- https://issues.liferay.com/browse/LPE-17448
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-42129
- http://liferay.com
