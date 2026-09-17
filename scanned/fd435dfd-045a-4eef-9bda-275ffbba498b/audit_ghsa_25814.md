# [M] Missing permission checks in Jekins Bitbucket Server Integration Plugin

## Summary
Severity: Medium
Advisory: GHSA-r5r6-v8qh-pmpq
CVE: CVE-2022-28134
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-r5r6-v8qh-pmpq
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:atlassian-bitbucket-server-integration` — affected >=0 <3.2.0

## Details
Jenkins Bitbucket Server Integration Plugin 3.1.0 and earlier does not perform permission checks in several HTTP endpoints, allowing attackers with Overall/Read permission to create, view, and delete BitBucket Server consumers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28134
- https://github.com/jenkinsci/atlassian-bitbucket-server-integration-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2640
- http://www.openwall.com/lists/oss-security/2022/03/29/1
