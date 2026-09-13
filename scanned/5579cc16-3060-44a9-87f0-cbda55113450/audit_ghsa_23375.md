# [M] Missing permission check in Jenkins Cloud Statistics Plugin

## Summary
Severity: Medium
Advisory: GHSA-xv69-6rf3-w5g2
CVE: CVE-2021-21631
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xv69-6rf3-w5g2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cloud-stats` — affected >=0 <0.27

## Details
Jenkins Cloud Statistics Plugin 0.26 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission and knowledge of random activity IDs to view related provisioning exception error messages.

Jenkins Cloud Statistics Plugin 0.27 requires Overall/Administer permission to access provisioning exception error messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21631
- https://github.com/jenkinsci/cloud-stats-plugin/commit/07dd3da346a65083a93a071036409f1128e0b133
- https://github.com/jenkinsci/cloud-stats-plugin
- https://www.jenkins.io/security/advisory/2021-03-30/#SECURITY-2246
- http://www.openwall.com/lists/oss-security/2021/03/30/1
