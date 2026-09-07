# [H] RabbitMQ HTTP API's queue deletion endpoint does not verify that the user has a required permission

## Summary
Severity: High
Advisory: GHSA-pj33-75x5-32j4
CVE: CVE-2024-51988
CWE: CWE-284
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-11-06
Source: https://github.com/advisories/GHSA-pj33-75x5-32j4
Type: github-advisory

## Affected
- Hex: `rabbit_common` — affected >=3.12.7 <3.12.11

## Details
### Summary

Queue deletion via the HTTP API was not verifying the `configure` permission of the user.

### Impact

Users who had all of the following:

1. Valid credentials
2. Some permissions for the target virtual host
3. HTTP API access 

could delete queues it had no (deletion) permissions for.

### Workarounds

Disable management plugin and use, for example, [Prometheus and Grafana](https://www.rabbitmq.com/docs/prometheus) for monitoring.

### OWASP Classification

OWASP Top10 A01:2021 – Broken Access Control

## References
- https://github.com/rabbitmq/rabbitmq-server/security/advisories/GHSA-pj33-75x5-32j4
- https://nvd.nist.gov/vuln/detail/CVE-2024-51988
- https://github.com/rabbitmq/rabbitmq-server
- https://www.rabbitmq.com/docs/prometheus
