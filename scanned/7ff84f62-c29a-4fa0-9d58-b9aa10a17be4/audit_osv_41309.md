# [M] Log4j2 AmqpAppender disables TLS hostname verification by default

## Summary
Severity: Medium
Advisory: CVE-2026-59272
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59272
Type: osv

## Details
Any application shipping logs to RabbitMQ over TLS via the Log4j2 appender, relying on the documented default, is exposed to man-in-the-middle interception of every log event.
Spring AMQP 4.1.0
Spring AMQP 4.0.0 - 4.0.4
Spring AMQP 3.2.0 - 3.2.12
Spring AMQP 2.4.18 and earlier

## References
- https://spring.io/security/cve-2026-59272
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59272.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59272
