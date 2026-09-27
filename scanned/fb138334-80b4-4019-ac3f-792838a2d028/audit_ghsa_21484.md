# [H] Path Traversal in Liferay Portal

## Summary
Severity: High
Advisory: GHSA-hffx-r282-w2g9
CVE: CVE-2022-42123
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-11-15
Source: https://github.com/advisories/GHSA-hffx-r282-w2g9
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.3.3 <7.4.3.19

## Details
A Zip slip vulnerability in the Elasticsearch Connector in Liferay Portal 7.3.3 through 7.4.3.18, and Liferay DXP 7.3 before update 6, and 7.4 before update 19 allows attackers to create or overwrite existing files on the filesystem via the installation of a malicious Elasticsearch Sidecar plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42123
- https://issues.liferay.com/browse/LPE-17518
- https://portal.liferay.dev/learn/security/known-vulnerabilities/-/asset_publisher/HbL5mxmVrnXW/content/cve-2022-42123
- http://liferay.com
