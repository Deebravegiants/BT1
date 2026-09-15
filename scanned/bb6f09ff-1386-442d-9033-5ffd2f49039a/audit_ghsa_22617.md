# [M] Liferay Portal and Liferay DXP May Reveal S3 Store's Proxy Password

## Summary
Severity: Medium
Advisory: GHSA-xx2h-2hf5-v7vv
CVE: CVE-2021-29043
CWE: CWE-200, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xx2h-2hf5-v7vv
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.0.0 <7.3.6
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.0.10.fp97
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp21
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp10
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.fp1

## Details
The Portal Store module in Liferay Portal 7.0.0 through 7.3.5, and Liferay DXP 7.0 before fix pack 97, 7.1 before fix pack 21, 7.2 before fix pack 10 and 7.3 before fix pack 1 does not obfuscate the S3 store's proxy password, which allows attackers to steal the proxy password via man-in-the-middle attacks or shoulder surfing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29043
- https://github.com/liferay/liferay-portal
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120743515
- https://web.archive.org/web/20210517183617/https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120743515
- http://liferay.com
