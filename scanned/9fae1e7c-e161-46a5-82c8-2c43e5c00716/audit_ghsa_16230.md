# [M] Liferay Portal and Liferay DXP Does Not Properly Restrict Membership to Child Site Based on Parent Site Options

## Summary
Severity: Medium
Advisory: GHSA-qpgh-6v9w-vfv6
CVE: CVE-2024-25149
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-qpgh-6v9w-vfv6
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.2.0 <7.4.2-ga3
- Maven: `com.liferay.portal:release.dxp.bom` — affected >=0 <7.2.10.fp15

## Details
Liferay Portal 7.2.0 through 7.4.1, and older unsupported versions, and Liferay DXP 7.3 before service pack 3, 7.2 before fix pack 15, and older unsupported versions does not properly restrict membership of a child site when the "Limit membership to members of the parent site" option is enabled, which allows remote authenticated users to add users who are not a member of the parent site to a child site. The added user may obtain permission to perform unauthorized actions in the child site.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25149
- https://github.com/liferay/liferay-portal/commit/dfd287acb325e2cddced3910e3baba1d258509de
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2024-25149
