# [M] Exposure of Sensitive Information to an Unauthorized Actor in Jenkins SSH Credentials Plugin

## Summary
Severity: Medium
Advisory: GHSA-cwcf-5m5w-mq2w
CVE: CVE-2018-1000601
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-cwcf-5m5w-mq2w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ssh-credentials` — affected >=0 <1.14
- Maven: `org.jenkins-ci.plugins:credentials` — affected >=0 <2.1.17

## Details
A arbitrary file read vulnerability exists in Jenkins SSH Credentials Plugin 1.13 and earlier in BasicSSHUserPrivateKey.java that allows attackers with a Jenkins account and the permission to configure credential bindings to read arbitrary files from the Jenkins master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000601
- https://github.com/jenkinsci/credentials-plugin/commit/23fbd6de33cc3cb74eafd44e7b27dd87b52c8904
- https://github.com/jenkinsci/ssh-credentials-plugin/commit/18b3121fa94a174064447d637dc11539e33b3a76
- https://github.com/jenkinsci/ssh-credentials-plugin
- https://github.com/jenkinsci/ssh-credentials-plugin/commits/ssh-credentials-1.14
- https://jenkins.io/security/advisory/2018-06-25/#SECURITY-440
