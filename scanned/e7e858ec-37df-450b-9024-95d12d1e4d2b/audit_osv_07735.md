# [C] Apache Tomcat: Bypass longest prefix security constraint

## Summary
Severity: Critical
Advisory: BIT-tomcat-2026-65182
Aliases: CVE-2026-65182, GHSA-gcx9-497g-6cp6
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-65182
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.25

## Details
Improper Access Control, Incorrect Authorization vulnerability in Apache Tomcat leads to security constraint bypass if a constraint for a longer path is specified before a more restrictive constraint for a shorter sub-path.



This issue affects Apache Tomcat: from 11.0.0 through 11.0.24, from 10.1.0 through 10.1.57, from 9.0.0 through 9.0.120, from 8.5.0 through 8.5.100, from 7.0.0 through 7.0.109.



Users are recommended to upgrade to version 11.0.25, 10.1.58, 9.0.121, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/26/1
- https://lists.apache.org/thread/joosxvzc9b49ttj8lj0jw9mqt0ml767m
- https://nvd.nist.gov/vuln/detail/CVE-2026-65182
