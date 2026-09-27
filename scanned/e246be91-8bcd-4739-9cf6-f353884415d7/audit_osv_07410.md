# [M] BIT-rabbitmq-c-2023-35789

## Summary
Severity: Medium
Advisory: BIT-rabbitmq-c-2023-35789
Aliases: CVE-2023-35789
Ecosystem: Bitnami
Published: 2026-03-20
Source: https://osv.dev/vulnerability/BIT-rabbitmq-c-2023-35789
Type: osv

## Affected
- Bitnami: `rabbitmq-c` — affected unspecified

## Details
An issue was discovered in the C AMQP client library (aka rabbitmq-c) through 0.13.0 for RabbitMQ. Credentials can only be entered on the command line (e.g., for amqp-publish or amqp-consume) and are thus visible to local attackers by listing a process and its arguments.

## References
- https://github.com/alanxz/rabbitmq-c/issues/575
- https://github.com/alanxz/rabbitmq-c/pull/781
- https://lists.debian.org/debian-lts-announce/2025/03/msg00022.html
- https://nvd.nist.gov/vuln/detail/CVE-2023-35789
