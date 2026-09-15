# [M] Missing permission checks in Zephyr for JIRA Test Management Plugin

## Summary
Severity: Medium
Advisory: GHSA-2q7j-52xg-x8fm
CVE: CVE-2020-2216
CWE: CWE-285, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2q7j-52xg-x8fm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:zephyr-for-jira-test-management` — affected >=0

## Details
A missing permission check in Jenkins Zephyr for JIRA Test Management Plugin 1.5 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified HTTP server using attacker-specified username and password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2216
- https://github.com/jenkinsci/zephyr-for-jira-test-management-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1762
- http://www.openwall.com/lists/oss-security/2020/07/02/7
