# [H] Liferay Portal defaults to a low work factor for the default password hashing algorithm

## Summary
Severity: High
Advisory: GHSA-43h9-p3j4-39hm
CVE: CVE-2024-25607
CWE: CWE-916
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-43h9-p3j4-39hm
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.u4
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.2.10.fp17
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.0 <7.4.13.u16
- Maven: `com.liferay.portal:release.portal.bom` — affected >=0 <7.4.3.14
- Maven: `com.liferay.portal:com.liferay.portal.kernel` — affected >=0 <38.0.0

## Details
The default password hashing algorithm (PBKDF2-HMAC-SHA1) in Liferay Portal 7.2.0 through 7.4.3.15, and older unsupported versions, and Liferay DXP 7.4 before update 16, 7.3 before update 4, 7.2 before fix pack 17, and older unsupported versions defaults to a low work factor, which allows attackers to quickly crack password hashes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25607
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2024-25607
