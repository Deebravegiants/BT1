# [M] Admin password disclosed in BrokerNotAliveException message

## Summary
Severity: Medium
Advisory: CVE-2026-59271
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59271
Type: osv

## Details
When the RabbitMQ management aliveness check fails, the configured admin password is embedded in cleartext in the thrown exception message.
Spring AMQP 4.1.0
Spring AMQP 4.0.0 - 4.0.4
Spring AMQP 3.2.0 - 3.2.12
Spring AMQP 2.4.18 and earlier

## References
- https://spring.io/security/cve-2026-59271
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59271.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59271
