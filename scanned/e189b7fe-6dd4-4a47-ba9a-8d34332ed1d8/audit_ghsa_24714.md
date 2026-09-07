# [M] Jenkins Job Import Plugin vulnerable to exposure of sensitive information

## Summary
Severity: Medium
Advisory: GHSA-57ww-2cvr-wv38
CVE: CVE-2019-1003016
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-57ww-2cvr-wv38
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:job-import-plugin` — affected >=0 <3.0

## Details
Jenkins Job Import Plugin did not check user permissions on its API endpoint used to access remote Jenkins instances. This allowed users with Overall/Read access to Jenkins to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Job Import Plugin 3.0 will only access Jenkins instances using credentials defined in the global configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003016
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-905%20(2)
