# [M] Liferay Portal and Liferay DXP Organization Selector Does Not Check User Permissions 

## Summary
Severity: Medium
Advisory: GHSA-xph3-vjcq-g488
CVE: CVE-2023-3426
CWE: CWE-425, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-08-02
Source: https://github.com/advisories/GHSA-xph3-vjcq-g488
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.organizations.item.selector.web` — affected >=0 <4.0.14
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.143.u81

## Details
The organization selector before 4.0.14 from Liferay Portal (7.4.3.81 through 7.4.3.85), and Liferay DXP 7.4 update 81 through 85 does not check user permission, which allows remote authenticated users to obtain a list of all organizations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3426
- https://github.com/liferay/liferay-portal/commit/b410f40233394d1d3d1076189befd4b33ba9fb47
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2023-3426
