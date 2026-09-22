# [M] Incorrect Authorization in Jenkins requests-plugin

## Summary
Severity: Medium
Advisory: GHSA-6xhf-xx3j-75f5
CVE: CVE-2022-34782
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-6xhf-xx3j-75f5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:requests` — affected >=0 <2.2.17

## Details
An incorrect permission check in Jenkins requests-plugin Plugin 2.2.16 and earlier allows attackers with Overall/Read permission to view the list of pending requests. requests-plugin Plugin 2.2.17 requires Overall/Administer permission to view the list of pending requests.

This is basically the same vulnerability as [SECURITY-1995](https://www.jenkins.io/security/advisory/2021-06-30/#SECURITY-1995), whose fix was ineffective.

requests-plugin Plugin 2.2.17 requires Overall/Administer permission to view the list of pending requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34782
- https://github.com/jenkinsci/requests-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2650
