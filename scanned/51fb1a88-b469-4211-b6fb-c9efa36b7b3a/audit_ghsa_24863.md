# [M] Jenkins SaltStack Plugin allows attackers to capture credentials with a known credentials ID stored in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-cqp4-cv7h-7jp5
CVE: CVE-2018-1999027
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-cqp4-cv7h-7jp5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:saltstack` — affected >=0 <3.1.7

## Details
An exposure of sensitive information vulnerability exists in Jenkins SaltStack Plugin 3.1.6 and earlier in SaltAPIBuilder.java, SaltAPIStep.java. SaltStack Plugin did not perform permission checks on methods implementing form validation. This allowed users with Overall/Read access to Jenkins to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins, and to cause Jenkins to submit HTTP requests to attacker-specified URLs. Additionally, these form validation methods did not require POST requests, resulting in a CSRF vulnerability. As of version 3.1.7, these form validation methods require POST requests and Overall/Administer permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999027
- https://github.com/jenkinsci/saltstack-plugin/commit/5306bcc438ff989e4b1999a0208fd6854979999b
- https://github.com/jenkinsci/saltstack-plugin
- https://jenkins.io/security/advisory/2018-07-30/#SECURITY-1009
