# [H] Liferay Portal and Liferay DXP autosaves form data for other users to see

## Summary
Severity: High
Advisory: GHSA-fxpf-jr2q-vpvv
CVE: CVE-2021-33323
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fxpf-jr2q-vpvv
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.dynamic.data.mapping.form.web` — affected >=0 <3.0.23
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp7

## Details
The Dynamic Data Mapping module in Dynamic Data Mapping Form Web before 3.0.23 in Liferay Portal 7.1.0 through 7.3.2, and Liferay DXP 7.1 before fix pack 19, and 7.2 before fix pack 7, autosaves form values for unauthenticated users, which allows remote attackers to view the autosaved values by viewing the form as an unauthenticated user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33323
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17049
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120747107
