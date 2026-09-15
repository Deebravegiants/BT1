# [H] Path traversal vulnerability in Jenkins agent names

## Summary
Severity: High
Advisory: GHSA-pxgq-gqr9-5gwx
CVE: CVE-2021-21605
CWE: CWE-20, CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pxgq-gqr9-5gwx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.263.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.264 <2.275

## Details
Jenkins 2.274 and earlier, LTS 2.263.1 and earlier allows users with Agent/Configure permission to choose agent names that cause Jenkins to override unrelated `config.xml` files. If the global `config.xml` file is replaced, Jenkins will start up with unsafe legacy defaults after a restart.

Jenkins 2.275, LTS 2.263.2 ensures that agent names are considered valid names for items to prevent this problem.

In case of problems, this change can be reverted by setting the [Java system property](https://www.jenkins.io/doc/book/managing/system-properties/) `jenkins.model.Nodes.enforceNameRestrictions` to `false`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21605
- https://github.com/jenkinsci/jenkins/commit/b19b34db4b24b163d4edc53ccb84f41a3589cb08
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-01-13/#SECURITY-2021
