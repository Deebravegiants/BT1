# [M] Jenkins Ansible Plugin man in the middle vulnerability

## Summary
Severity: Medium
Advisory: GHSA-322x-jv5h-cvjh
CVE: CVE-2018-1000149
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-322x-jv5h-cvjh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ansible` — affected >=0 <1.0

## Details
A man in the middle vulnerability exists in Jenkins Ansible Plugin 0.8 and older in `AbstractAnsibleInvocation.java`, `AnsibleAdHocCommandBuilder.java`, `AnsibleAdHocCommandInvocationTest.java`, `AnsibleContext.java`, `AnsibleJobDslExtension.java`, `AnsiblePlaybookBuilder.java`, `AnsiblePlaybookStep.java` that disables host key verification by default. Ansible Plugin 1.0 now enables host key verification by default, adding options allowing users to opt out.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000149
- https://github.com/jenkinsci/ansible-plugin/commit/06d30e5b626a978e258a7f4ab473cd7f53a7cba7
- https://jenkins.io/security/advisory/2018-03-26/#SECURITY-630
