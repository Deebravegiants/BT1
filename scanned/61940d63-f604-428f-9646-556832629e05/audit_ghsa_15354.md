# [M] Jenkins does not perform a permission check in an HTTP endpoint

## Summary
Severity: Medium
Advisory: GHSA-8pv9-qh96-9hc6
CVE: CVE-2024-43045
CWE: CWE-285, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-07
Source: https://github.com/advisories/GHSA-8pv9-qh96-9hc6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.452.4
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.460 <2.462.1
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.470 <2.471

## Details
Jenkins 2.470 and earlier, LTS 2.452.3 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to access other users' "My Views". Attackers with global View/Configure and View/Delete permissions are also able to change other users' "My Views".

Jenkins 2.471, LTS 2.452.4, LTS 2.462.1 restricts access to a user’s "My Views" to the owning user and administrators.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43045
- https://github.com/jenkinsci/jenkins/commit/0c13259cebc6a780fee7825838f4dd98ece8e68a
- https://github.com/jenkinsci/jenkins/commit/3752f406bfef764e4954238acf44343169ae5799
- https://github.com/jenkinsci/jenkins/commit/efece77d759b38c95b39b191051a8203bbc2f428
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2024-08-07/#SECURITY-3349
