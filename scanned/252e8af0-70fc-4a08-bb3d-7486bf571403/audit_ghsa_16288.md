# [M] Liferay Portal denial-of-service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w275-m8cr-hf2v
CVE: CVE-2024-25144
CWE: CWE-834, CWE-835
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2024-02-08
Source: https://github.com/advisories/GHSA-w275-m8cr-hf2v
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.2.0 <7.4.3.27
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp19
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.u6
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.4.0 <7.4.13.u27

## Details
The IFrame widget in Liferay Portal 7.2.0 through 7.4.3.26, and older unsupported versions, and Liferay DXP 7.4 before update 27, 7.3 before update 6, 7.2 before fix pack 19, and older unsupported versions does not check the URL of the IFrame, which allows remote authenticated users to cause a denial-of-service (DoS) via a self referencing IFrame.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25144
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2024-25144
