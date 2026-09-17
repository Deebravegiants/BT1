# [M] Arbitrary file read vulnerability in Jenkins AWS CodeCommit Trigger Plugin

## Summary
Severity: Medium
Advisory: GHSA-whgj-6m78-2gg9
CVE: CVE-2023-35147
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-whgj-6m78-2gg9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:aws-codecommit-trigger` — affected >=0

## Details
Jenkins AWS CodeCommit Trigger Plugin 3.0.12 and earlier does not restrict the AWS SQS queue name path parameter in an HTTP endpoint, allowing attackers with Item/Read permission to obtain the contents of arbitrary files on the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35147
- https://www.jenkins.io/security/advisory/2023-06-14/#SECURITY-3099
- http://www.openwall.com/lists/oss-security/2023/06/14/5
