# [M] Liferay Portal and Liferay DXP Information Disclosure Vulnerability in the Control Panel

## Summary
Severity: Medium
Advisory: GHSA-4585-28v2-8h46
CVE: CVE-2024-25150
CWE: CWE-201
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-4585-28v2-8h46
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.2.0 <7.4.3.4-ga4
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.2.10.fp19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.u4

## Details
Information disclosure vulnerability in the Control Panel in Liferay Portal 7.2.0 through 7.4.2, and older unsupported versions, and Liferay DXP 7.3 before update 4, 7.2 before fix pack 19, and older unsupported versions allows remote authenticated users to obtain a user's full name from the page's title by enumerating user screen names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25150
- https://github.com/liferay/liferay-portal/commit/12844a327061ad55e560f5ab7056381e9cc05d86
- https://github.com/liferay/liferay-portal/commit/8eba0b84a0967ad785d96cb09f41f3fac998dcfc
- https://github.com/liferay/liferay-portal/commit/9d7676866a77c910a7cf689e33c621666bff9a04
- https://github.com/liferay/liferay-portal/commit/c5fa9c50514d2be0191cb076b8744c7a871f23dc
- https://github.com/liferay/liferay-portal/commit/eee01ec6cce3cca99c9e12fba846db1fc64d610d
- https://github.com/liferay/liferay-portal/commit/f9d6c9b9551956c6f07d4ae8998f53392e3389c0
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2024-25150
