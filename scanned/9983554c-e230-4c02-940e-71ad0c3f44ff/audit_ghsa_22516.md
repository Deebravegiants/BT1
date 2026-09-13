# [H] Apache Wicket Sensitive Data Exposure

## Summary
Severity: High
Advisory: GHSA-q7wx-mhx4-jr8q
CVE: CVE-2014-3526
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-q7wx-mhx4-jr8q
Type: github-advisory

## Affected
- Maven: `org.apache.wicket:wicket-core` — affected >=0 <1.5.12
- Maven: `org.apache.wicket:wicket-core` — affected >=6.0 <6.17.0
- Maven: `org.apache.wicket:wicket-core` — affected >=7.0.0-M1 <7.0.0-M3

## Details
Apache Wicket before 1.5.12, 6.x before 6.17.0, and 7.x before 7.0.0-M3 might allow remote attackers to obtain sensitive information via vectors involving identifiers for storing page markup for temporary user sessions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3526
- https://wicket.apache.org/news/2014/09/22/cve-2014-3526.html
