# [M] Liferay Portal ComboServlet denial of service via large file combination

## Summary
Severity: Medium
Advisory: GHSA-q95h-87j6-273x
CVE: CVE-2025-62254
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-24
Source: https://github.com/advisories/GHSA-q95h-87j6-273x
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:com.liferay.portal.impl` — affected >=0 <97.0.0

## Details
The ComboServlet in Liferay Portal 7.4.0 through 7.4.3.111, and older unsupported versions, and Liferay DXP 2023.Q4.0 through 2023.Q4.2, 2023.Q3.1 through 2023.Q3.5, 7.4 GA through update 92, 7.3 GA through update 35, and older unsupported versions  does not limit the number or size of the files it will combine, which allows remote attackers to create very large responses that lead to a denial of service attack via the URL query string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62254
- https://github.com/liferay/liferay-portal/commit/45e1a3a757bc38f7b9f8034909e90f1a56f160a5
- https://github.com/liferay/liferay-portal/commit/8328aaf7c6ebb3f76c7982256e028caeb48fb664
- https://github.com/liferay/liferay-portal/commit/85d63e9d6e47e11074046cc4459d3b1ab3370536
- https://github.com/liferay/liferay-portal/commit/def502837297d155ec2fd61044288e75230dd235
- https://github.com/liferay/liferay-portal
- https://liferay.atlassian.net/browse/LPE-17867
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-62254
