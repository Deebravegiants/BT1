# [M] Jakarta Apache Tomcat Reveals Physical Paths

## Summary
Severity: Medium
Advisory: GHSA-qg4g-6jcq-rw93
CVE: CVE-2000-0759
CWE: CWE-200
Ecosystem: Maven
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-qg4g-6jcq-rw93
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=0

## Details
Jakarta Tomcat 3.1 under Apache reveals physical path information when a remote attacker requests a URL that does not exist, which generates an error message that includes the physical path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2000-0759
