# [M] Lack of type validation in agent related REST API in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-pvwx-3jx5-24r2
CVE: CVE-2021-21639
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pvwx-3jx5-24r2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.277.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.278 <2.287

## Details
Jenkins 2.286 and earlier, LTS 2.277.1 and earlier does not validate the type of object created after loading the data submitted to the `config.xml` REST API endpoint of a node.

This allows attackers with Computer/Configure permission to replace a node with one of a different type.

Jenkins 2.287, LTS 2.277.2 validates the type of object created and rejects objects of unexpected types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21639
- https://github.com/jenkinsci/jenkins/commit/84210baed0c866bdee3e59271f98a767a14a5509
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-04-07/#SECURITY-1721
- http://www.openwall.com/lists/oss-security/2021/04/07/2
