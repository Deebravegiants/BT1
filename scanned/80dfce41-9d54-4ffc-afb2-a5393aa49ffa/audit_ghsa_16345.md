# [M] Liferay Portal and Liferay DXP HTTP Header Can Expose Versions

## Summary
Severity: Medium
Advisory: GHSA-2mvj-q2q3-wxjv
CVE: CVE-2024-26267
CWE: CWE-1188
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-2mvj-q2q3-wxjv
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.2.0 <7.4.3.26-ga26
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.2.10.fp19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.u5
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.0 <7.4.13.u26

## Details
In Liferay Portal 7.2.0 through 7.4.3.25, and older unsupported versions, and Liferay DXP 7.4 before update 26, 7.3 before update 5, 7.2 before fix pack 19, and older unsupported versions the default value of the portal property `http.header.version.verbosity` is set to `full`, which allows remote attackers to easily identify the version of the application that is running and the vulnerabilities that affect that version via 'Liferay-Portal` response header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-26267
- https://github.com/liferay/liferay-portal/commit/00750dade0cc81efc380fcc6d7e2f58060c4ad95
- https://github.com/liferay/liferay-portal/commit/0e881cac66db14a11673c0352def6df04f77d35c
- https://github.com/liferay/liferay-portal/commit/9658cec331feaaaad8bf93c6f65e1768a1f43ae2
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2024-26267
