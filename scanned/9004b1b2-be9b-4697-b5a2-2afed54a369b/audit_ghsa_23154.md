# [H] Inbound TCP Agent Protocol/3 authentication bypass in Jenkins

## Summary
Severity: High
Advisory: GHSA-qp4f-2w67-c8hw
CVE: CVE-2020-2099
CWE: CWE-323, CWE-330
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qp4f-2w67-c8hw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.204.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.205 <2.214

## Details
Jenkins 2.213 and earlier, LTS 2.204.1 and earlier includes support for the Inbound TCP Agent Protocol/3 for communication between controller and agents. While [this protocol has been deprecated in 2018](https://www.jenkins.io/changelog-old/#v2.128) and was recently removed from Jenkins in 2.214, it could still easily be enabled in Jenkins LTS 2.204.1, 2.213, and older.

This protocol incorrectly reuses encryption parameters which allow an unauthenticated remote attacker to determine the connection secret. This secret can then be used to connect attacker-controlled Jenkins agents to the Jenkins controller.

Jenkins 2.204.2 no longer allows for the use of Inbound TCP Agent Protocol/3 by default. The system property `jenkins.slaves.JnlpSlaveAgentProtocol3.ALLOW_UNSAFE` can be set to `true` to allow enabling the Inbound TCP Agent Protocol/3 in Jenkins 2.204.2, but doing so is strongly discouraged.

Inbound TCP Agent Protocol/3 was removed completely from Jenkins 2.214 and will not be part of Jenkins LTS after the end of the 2.204.x line.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2099
- https://github.com/jenkinsci/jenkins/commit/5054bc6e12e1022993d719f66e289ab1d22ae854
- https://access.redhat.com/errata/RHBA-2020:0402
- https://access.redhat.com/errata/RHBA-2020:0675
- https://access.redhat.com/errata/RHSA-2020:0681
- https://access.redhat.com/errata/RHSA-2020:0683
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2020-01-29/#SECURITY-1682
- http://www.openwall.com/lists/oss-security/2020/01/29/1
