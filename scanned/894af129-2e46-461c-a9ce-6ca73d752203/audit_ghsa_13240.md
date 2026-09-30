# [M] Missing permission check in Jenkins AWS CodeCommit Trigger Plugin allows enumerating credentials IDs

## Summary
Severity: Medium
Advisory: GHSA-pfg6-cj3j-rpv4
CVE: CVE-2023-41941
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-pfg6-cj3j-rpv4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:aws-codecommit-trigger` — affected >=0

## Details
A missing permission check in Jenkins AWS CodeCommit Trigger Plugin 3.0.12 and earlier allows attackers with Overall/Read permission to enumerate credentials IDs of AWS credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41941
- https://www.jenkins.io/security/advisory/2023-09-06/#SECURITY-3101%20(1)
- http://www.openwall.com/lists/oss-security/2023/09/06/9
