# [M] Jenkins does not exclude sensitive build variables from search

## Summary
Severity: Medium
Advisory: GHSA-279f-qwgh-h5mp
CVE: CVE-2023-43494
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-279f-qwgh-h5mp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.50 <2.414.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.415 <2.424

## Details
Jenkins allows filtering builds in the build history widget by specifying an expression that searches for matching builds by name, description, parameter values, etc.

Jenkins 2.50 through 2.423 (both inclusive), LTS 2.60.1 through 2.414.1 (both inclusive) does not exclude sensitive build variables (e.g., password parameter values) from this search.

This allows attackers with Item/Read permission to obtain values of sensitive variables used in builds by iteratively testing different characters until the correct sequence is discovered.

Jenkins 2.424, LTS 2.414.2 excludes sensitive variables from this search.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43494
- https://github.com/jenkinsci/jenkins/commit/b8ac8cd4c51511b9f844846ba80a8aed054288c5
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2023-09-20/#SECURITY-3261
- http://www.openwall.com/lists/oss-security/2023/09/20/5
