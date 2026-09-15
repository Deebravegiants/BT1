# [H] Liferay Portal Layout Module and Liferay DXP Exposes the Cross-Site Request Forgery (CSRF) Token in URLs

## Summary
Severity: High
Advisory: GHSA-4frg-rpx6-96qh
CVE: CVE-2021-33338
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4frg-rpx6-96qh
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.1.0 <7.3.3
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.1.0 <7.1.10.fp19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp6

## Details
The Layout module in Liferay Portal 7.1.0 through 7.3.2, and Liferay DXP 7.1 before fix pack 19, and 7.2 before fix pack 6, exposes the CSRF token in URLs, which allows man-in-the-middle attackers to obtain the token and conduct Cross-Site Request Forgery (CSRF) attacks via the p_auth parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33338
- https://github.com/liferay/liferay-portal
- https://issues.liferay.com/browse/LPE-17030
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/id/120748276
