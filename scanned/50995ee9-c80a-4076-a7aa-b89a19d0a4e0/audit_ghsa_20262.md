# [M] Cross-Site Request Forgery in Jenkins ThreadFix Plugin

## Summary
Severity: Medium
Advisory: GHSA-rq99-93c5-33f6
CVE: CVE-2022-34209
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-rq99-93c5-33f6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:threadfix` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins ThreadFix Plugin 1.5.4 and earlier allows attackers to connect to an attacker-specified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34209
- https://github.com/jenkinsci/threadfix-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2249
