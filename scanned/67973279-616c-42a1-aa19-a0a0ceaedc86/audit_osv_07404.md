# [M] BIT-rabbitmq-2020-5419

## Summary
Severity: Medium
Advisory: BIT-rabbitmq-2020-5419
Aliases: CVE-2020-5419
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-rabbitmq-2020-5419
Type: osv

## Affected
- Bitnami: `rabbitmq` — affected >=3.8.0 <3.8.7

## Details
RabbitMQ versions 3.8.x prior to 3.8.7 are prone to a Windows-specific binary planting security vulnerability that allows for arbitrary code execution. An attacker with write privileges to the RabbitMQ installation directory and local access on Windows could carry out a local binary hijacking (planting) attack and execute arbitrary code.

## References
- https://tanzu.vmware.com/security/cve-2020-5419
