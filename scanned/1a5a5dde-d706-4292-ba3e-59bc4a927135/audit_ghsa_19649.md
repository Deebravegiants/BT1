# [M] Jenkins reveals encrypted values of secrets stored in agent configuration to users with Agent/Extended Read permission

## Summary
Severity: Medium
Advisory: GHSA-p34j-r3ch-c985
CVE: CVE-2025-27622
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-03-06
Source: https://github.com/advisories/GHSA-p34j-r3ch-c985
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.493 <2.500
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.492.2

## Details
Jenkins 2.499 and earlier, LTS 2.492.1 and earlier does not redact encrypted values of secrets when accessing `config.xml` of agents via REST API or CLI.

This allows attackers with Agent/Extended Read permission to view encrypted values of secrets.

Jenkins 2.500, LTS 2.492.2 redacts the encrypted values of secrets stored in agent `config.xml` accessed via REST API or CLI for users lacking Agent/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27622
- https://github.com/jenkinsci/jenkins/commit/923cdbc165e8b8523ae960dfee5f7354878532d5
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2025-03-05/#SECURITY-3495
