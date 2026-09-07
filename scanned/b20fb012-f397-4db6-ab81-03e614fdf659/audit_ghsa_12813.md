# [H] Cross-site request forgery vulnerability in Jenkins RabbitMQ Consumer Plugin

## Summary
Severity: High
Advisory: GHSA-wj79-9fxj-j86p
CVE: CVE-2023-24447
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-wj79-9fxj-j86p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rabbitmq-consumer` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins RabbitMQ Consumer Plugin 2.8 and earlier allows attackers to connect to an attacker-specified AMQP(S) URL using attacker-specified username and password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24447
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2778
