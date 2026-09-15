# [H] Agent-to-controller security bypass in Jenkins Squash TM Publisher (Squash4Jenkins) Plugin allows writing arbitrary files

## Summary
Severity: High
Advisory: GHSA-h648-gj34-5x4r
CVE: CVE-2021-43578
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h648-gj34-5x4r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:squashtm-publisher-plugin` — affected >=0

## Details
Jenkins Squash TM Publisher (Squash4Jenkins) Plugin 1.0.0 and earlier implements an agent-to-controller message that does not implement any validation of its input, allowing attackers able to control agent processes to replace arbitrary files on the Jenkins controller file system with an attacker-controlled JSON string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43578
- https://github.com/jenkinsci/squashtm-publisher-plugin
- https://www.jenkins.io/security/advisory/2021-11-12/#SECURITY-2525
- http://www.openwall.com/lists/oss-security/2021/11/12/1
