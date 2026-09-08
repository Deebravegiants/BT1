# [M] Missing permission check in Jenkins ThreadFix Plugin

## Summary
Severity: Medium
Advisory: GHSA-77vq-4j66-46m5
CVE: CVE-2022-34210
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-77vq-4j66-46m5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:threadfix` — affected >=0

## Details
A missing permission check in Jenkins ThreadFix Plugin 1.5.4 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34210
- https://github.com/jenkinsci/threadfix-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2249
