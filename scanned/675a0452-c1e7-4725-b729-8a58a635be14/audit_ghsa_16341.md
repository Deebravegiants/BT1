# [M] Liferay Portal allows attackers to discover the existence of sites

## Summary
Severity: Medium
Advisory: GHSA-mqf8-4cqm-p83x
CVE: CVE-2024-25146
CWE: CWE-203, CWE-204
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-08
Source: https://github.com/advisories/GHSA-mqf8-4cqm-p83x
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.2.0 <7.4.2
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.3.0 <7.3.10.u4
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=7.2.0 <7.2.10.fp18

## Details
Liferay Portal 7.2.0 through 7.4.1, and older unsupported versions, and Liferay DXP 7.3 before service pack 3, 7.2 before fix pack 18, and older unsupported versions returns with different responses depending on whether a site does not exist or if the user does not have permission to access the site, which allows remote attackers to discover the existence of sites by enumerating URLs. This vulnerability occurs if locale.prepend.friendly.url.style=2 and if a custom 404 page is used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25146
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2024-25146
