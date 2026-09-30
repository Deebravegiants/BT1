# [M] Missing Authorization in jenkins xray-connector

## Summary
Severity: Medium
Advisory: GHSA-5557-j87h-cvf4
CVE: CVE-2021-21653
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-5557-j87h-cvf4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:xray-connector` — affected >=0 <2.4.1

## Details
Jenkins Xray - Test Management for Jira Plugin 2.4.0 and earlier does not perform a permission check in an HTTP endpoint, allowing with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21653
- https://www.jenkins.io/security/advisory/2021-05-11/#SECURITY-2251%20(2)
