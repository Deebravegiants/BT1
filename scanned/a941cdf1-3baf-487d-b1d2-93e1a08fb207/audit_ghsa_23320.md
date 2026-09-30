# [M] Incomplete List of Disallowed Inputs in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-ffgg-vphh-v273
CVE: CVE-2017-2602
CWE: CWE-184
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-ffgg-vphh-v273
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.32.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.34 <2.44

## Details
Jenkins before versions 2.44 and 2.32.2 is vulnerable to an improper blacklisting of the Pipeline metadata files in the agent-to-master security subsystem. This could allow metadata files to be written to by malicious agents (SECURITY-358).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2602
- https://github.com/jenkinsci/jenkins/commit/414ff7e30aba66bed18c4ee8a8660fb36fc8c655
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2602
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2017-02-01
