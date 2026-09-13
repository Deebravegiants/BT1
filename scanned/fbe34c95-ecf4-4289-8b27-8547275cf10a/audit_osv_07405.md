# [H] BIT-rabbitmq-2021-22116

## Summary
Severity: High
Advisory: BIT-rabbitmq-2021-22116
Aliases: CVE-2021-22116
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-rabbitmq-2021-22116
Type: osv

## Affected
- Bitnami: `rabbitmq` — affected >=0 <3.8.16

## Details
RabbitMQ all versions prior to 3.8.16 are prone to a denial of service vulnerability due to improper input validation in AMQP 1.0 client connection endpoint. A malicious user can exploit the vulnerability by sending malicious AMQP messages to the target RabbitMQ instance having the AMQP 1.0 plugin enabled.

## References
- https://lists.debian.org/debian-lts-announce/2021/07/msg00011.html
- https://tanzu.vmware.com/security/cve-2021-22116
- https://nvd.nist.gov/vuln/detail/CVE-2021-22116
