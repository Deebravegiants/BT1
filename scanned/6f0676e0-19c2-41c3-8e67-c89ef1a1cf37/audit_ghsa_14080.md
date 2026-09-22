# [M] Liferay Portal has Inefficient Regular Expression

## Summary
Severity: Medium
Advisory: GHSA-chrc-q6v3-jfv8
CVE: CVE-2023-33950
CWE: CWE-1333
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-24
Source: https://github.com/advisories/GHSA-chrc-q6v3-jfv8
Type: github-advisory

## Affected
- Maven: `com.liferay.portal:release.portal.bom` — affected >=7.4.3.48 <7.4.3.77

## Details
Pattern Redirects in Liferay Portal 7.4.3.48 through 7.4.3.76, and Liferay DXP 7.4 update 48 through 76 allows regular expressions that are vulnerable to ReDoS attacks to be used as patterns, which allows remote attackers to consume an excessive amount of server resources via crafted request URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33950
- https://github.com/liferay/liferay-portal
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/cve-2023-33950
