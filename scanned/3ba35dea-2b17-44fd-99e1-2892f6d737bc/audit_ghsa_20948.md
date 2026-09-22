# [M] Jenkins WildFly Deployer Plugin vulnerable to path traversal

## Summary
Severity: Medium
Advisory: GHSA-f7fq-wp2x-jc25
CVE: CVE-2022-41235
CWE: CWE-22, CWE-284, CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-f7fq-wp2x-jc25
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:wildfly-deployer` — affected >=0

## Details
Jenkins WildFly Deployer Plugin 1.0.2 and earlier implements functionality that allows agent processes to read arbitrary files on the Jenkins controller file system.

This vulnerability is only exploitable in Jenkins 2.318 and earlier, LTS 2.303.2 and earlier. See the [LTS upgrade guide](https://www.jenkins.io/doc/upgrade-guide/2.303/#upgrading-to-jenkins-lts-2-303-3).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41235
- https://github.com/jenkinsci/wildfly-deployer-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2645
