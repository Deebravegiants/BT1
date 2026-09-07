# [H] CSRF vulnerability and missing permission checks in Jenkins AbsInt Astrée Plugin

## Summary
Severity: High
Advisory: GHSA-c9px-7j36-f35v
CVE: CVE-2018-1000189
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-c9px-7j36-f35v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:absint-astree` — affected >=0 <1.0.7

## Details
A command execution vulnerability exists in Jenkins Absint Astree Plugin 1.0.5 and older in AstreeBuilder.java that allows attackers with Overall/Read access to execute a command on the Jenkins master.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000189
- https://jenkins.io/security/advisory/2018-06-04/#SECURITY-807
