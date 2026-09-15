# [M] Liferay Portal and Liferay DXP's HtmlUtil.escapeRedirect Can Be Circumvented via Replacement Character

## Summary
Severity: Medium
Advisory: GHSA-548x-j6x6-hcv4
CVE: CVE-2024-25608
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-548x-j6x6-hcv4
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.2.0 <7.4.3.19-ga19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.2.10.fp19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.u4
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.0 <7.4.13.u19

## Details
HtmlUtil.escapeRedirect in Liferay Portal 7.2.0 through 7.4.3.18, and older unsupported versions, and Liferay DXP 7.4 before update 19, 7.3 before update 4, 7.2 before fix pack 19, and older unsupported versions can be circumvented by using the 'REPLACEMENT CHARACTER' (U+FFFD), which allows remote attackers to redirect users to arbitrary external URLs via the (1) 'redirect` parameter (2) `FORWARD_URL` parameter, (3) `noSuchEntryRedirect` parameter, and (4) others parameters that rely on HtmlUtil.escapeRedirect.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25608
- https://github.com/liferay/liferay-portal/commit/36adf82ef7a09c7035d4f19a1982dcde1ae3f6ae
- https://github.com/liferay/liferay-portal/commit/aea651fa5110934b6a00d93391fac87985e27786
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2024-25608
