# [M] Liferay Portal and DXP use an incorrect cache-control header

## Summary
Severity: Medium
Advisory: GHSA-6533-fhr2-f38h
CVE: CVE-2025-62276
CWE: CWE-525
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-11-01
Source: https://github.com/advisories/GHSA-6533-fhr2-f38h
Type: github-advisory

## Affected
- Maven: `com.liferay:com.liferay.adaptive.media.web` — affected >=0 <5.0.52
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <69.1.0

## Details
The Document Library and the Adaptive Media modules in Liferay Portal 7.4.0 through 7.4.3.111, and older unsupported versions, and Liferay DXP 2023.Q4.0 through 2023.Q4.10, 2023.Q3.1 through 2023.Q3.10, 7.4 GA through update 92, and older unsupported versions uses an incorrect cache-control header, which allows local users to obtain access to downloaded files via the browser's cache.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62276
- https://github.com/liferay/liferay-portal/commit/36c080fc4522e46d69b5c3b4b9eb6aca5ff52699
- https://github.com/liferay/liferay-portal/commit/9781b594cffcd23583a1a0f93746fd20e3eb55bd
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17701
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62276
