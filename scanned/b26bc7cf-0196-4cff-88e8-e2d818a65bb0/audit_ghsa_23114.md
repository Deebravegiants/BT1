# [M] Missing permission check in Jenkins Pipeline Maven Integration Plugin allows enumerating credentials IDs

## Summary
Severity: Medium
Advisory: GHSA-32xp-m6vg-gwpj
CVE: CVE-2020-2233
CWE: CWE-285, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-32xp-m6vg-gwpj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-maven` — affected >=0 <3.8.3

## Details
Pipeline Maven Integration Plugin 3.8.2 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read access to Jenkins to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of credentials IDs in Pipeline Maven Integration Plugin 3.8.3 requires the appropriate permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2233
- https://github.com/jenkinsci/pipeline-maven-plugin
- https://jenkins.io/security/advisory/2020-08-12/#SECURITY-1794%20(1)
- http://www.openwall.com/lists/oss-security/2020/08/12/4
