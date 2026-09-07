# [H] Open Redirect in Liferay Portal

## Summary
Severity: High
Advisory: GHSA-mg53-xr8m-86hw
CVE: CVE-2020-24554
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-mg53-xr8m-86hw
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.3.3

## Details
The redirect module in Liferay Portal before 7.3.3 does not limit the number of URLs resulting in a 404 error that is recorded, which allows remote attackers to perform a denial of service attack by making repeated requests for pages that do not exist.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24554
- https://portal.liferay.dev/learn/security/known-vulnerabilities
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/119784956
