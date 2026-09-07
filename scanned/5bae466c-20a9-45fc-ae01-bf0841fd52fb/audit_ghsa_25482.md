# [M] JBoss EJB Client information disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2259-h742-5vr4
CVE: CVE-2021-20250
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2259-h742-5vr4
Type: github-advisory

## Affected
- Maven: `org.jboss:jboss-ejb-client` — affected >=0 <4.0.39

## Details
A flaw was found in wildfly. The JBoss EJB client has publicly accessible privileged actions which may lead to information disclosure on the server it is deployed on. The highest threat from this vulnerability is to data confidentiality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20250
- https://bugzilla.redhat.com/show_bug.cgi?id=1929479
