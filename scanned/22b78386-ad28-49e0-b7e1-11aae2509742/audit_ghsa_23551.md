# [M] Missing permission check in Jenkins requests-plugin Plugin allows sending emails

## Summary
Severity: Medium
Advisory: GHSA-w3gm-vv58-wr55
CVE: CVE-2021-21676
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w3gm-vv58-wr55
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:requests` — affected >=0 <2.2.8

## Details
Jenkins requests-plugin Plugin 2.2.7 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to send test emails to an attacker-specified email address.

Jenkins requests-plugin Plugin 2.2.8 requires Overall/Administer permission to send test emails.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21676
- https://github.com/jenkinsci/requests-plugin
- https://www.jenkins.io/security/advisory/2021-06-30/#SECURITY-2136%20%282%29
- https://www.jenkins.io/security/advisory/2021-06-30/#SECURITY-2136%20(2)
- http://www.openwall.com/lists/oss-security/2021/06/30/1
