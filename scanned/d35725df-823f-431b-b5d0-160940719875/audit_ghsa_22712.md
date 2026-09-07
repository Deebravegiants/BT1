# [M] Liferay DXP Vulnerable to Cross-Site Scripting (XSS) via the currentURL Parameter

## Summary
Severity: Medium
Advisory: GHSA-w28v-87g6-cjr6
CVE: CVE-2021-29049
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w28v-87g6-cjr6
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.0 <7.0.10.fp99
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp23
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp12
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.fp1

## Details
Cross-site scripting (XSS) vulnerability in the Portal Workflow module's edit process page in Liferay DXP 7.0 before fix pack 99, 7.1 before fix pack 23, 7.2 before fix pack 12 and 7.3 before fix pack 1, allows remote attackers to inject arbitrary web script or HTML via the currentURL parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29049
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17211
- http://liferay.com
