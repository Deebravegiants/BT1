# [M] Missing permission check in Jenkins RabbitMQ Consumer Plugin

## Summary
Severity: Medium
Advisory: GHSA-qgjq-hrhg-f24h
CVE: CVE-2023-24448
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-qgjq-hrhg-f24h
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rabbitmq-consumer` — affected >=0

## Details
A missing permission check in Jenkins RabbitMQ Consumer Plugin 2.8 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified AMQP(S) URL using attacker-specified username and password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24448
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2778
