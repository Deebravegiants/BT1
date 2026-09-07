# [M] Missing permission check in Jenkins Liquibase Runner Plugin allows enumerating credentials IDs

## Summary
Severity: Medium
Advisory: GHSA-44cm-p9q7-rr3p
CVE: CVE-2020-2285
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-44cm-p9q7-rr3p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:liquibase-runner` — affected >=0 <1.4.8

## Details
Liquibase Runner Plugin 1.4.7 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of credentials IDs in Liquibase Runner Plugin 1.4.8 requires the appropriate permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2285
- https://github.com/jenkinsci/liquibase-runner-plugin/commit/d1607478c9592f45d5e9a4868cb85195c634cb60
- https://github.com/jenkinsci/liquibase-runner-plugin
- https://www.jenkins.io/security/advisory/2020-09-23/#SECURITY-2030
- http://www.openwall.com/lists/oss-security/2020/09/23/1
