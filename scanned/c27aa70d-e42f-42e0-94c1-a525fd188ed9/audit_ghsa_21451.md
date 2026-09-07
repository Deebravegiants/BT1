# [M] Missing permissions check in Liferay Portal

## Summary
Severity: Medium
Advisory: GHSA-642h-mx8q-47p2
CVE: CVE-2022-42126
CWE: CWE-280, CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-11-15
Source: https://github.com/advisories/GHSA-642h-mx8q-47p2
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.3.5 <7.4.3.48

## Details
The Asset Libraries module in Liferay Portal 7.3.5 through 7.4.3.28, and Liferay DXP 7.3 before update 8, and DXP 7.4 before update 29 does not properly check permissions of asset libraries, which allows remote authenticated users to view asset libraries via the UI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42126
- https://issues.liferay.com/browse/LPE-17593
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-42126
- http://liferay.com
