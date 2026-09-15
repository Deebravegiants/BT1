# [H] Liferay Portal and Liferay DXP Fails to Invalidate CAPTCHA Answers After Use

## Summary
Severity: High
Advisory: GHSA-9mxg-p873-6793
CVE: CVE-2021-29047
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9mxg-p873-6793
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.3.4 <7.3.6
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.3.10.fp1

## Details
The SimpleCaptcha implementation in Liferay Portal 7.3.4, 7.3.5 and Liferay DXP 7.3 before fix pack 1 does not invalidate CAPTCHA answers after it is used, which allows remote attackers to repeatedly perform actions protected by a CAPTCHA challenge by reusing the same CAPTCHA answer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29047
- https://github.com/liferay/liferay-portal
- https://web.archive.org/web/20210524180455/https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120743467
- http://liferay.com
