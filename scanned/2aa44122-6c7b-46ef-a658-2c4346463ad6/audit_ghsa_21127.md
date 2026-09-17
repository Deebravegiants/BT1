# [H] SQL Injection found in Dataease 

## Summary
Severity: High
Advisory: GHSA-hmvw-66jm-h9fh
CVE: CVE-2022-34114
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-23
Source: https://github.com/advisories/GHSA-hmvw-66jm-h9fh
Type: github-advisory

## Affected
- Maven: `io.dataease:dataease-plugin-common` — affected >=0 <1.11.2

## Details
Dataease v1.11.1 was discovered to contain a SQL injection vulnerability via the parameter `dataSourceId`. Version 1.11.2 contains a fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34114
- https://github.com/dataease/dataease/issues/2430
- https://github.com/dataease/dataease
- https://github.com/dataease/dataease/releases/tag/v1.11.2
