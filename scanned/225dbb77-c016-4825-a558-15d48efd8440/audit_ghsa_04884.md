# [M] RabbitMQ vulnerable to Denial of Service by publishing large messages over the HTTP API

## Summary
Severity: Medium
Advisory: GHSA-w6cq-9cf4-gqpg
CVE: CVE-2023-46118
CWE: CWE-400
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-w6cq-9cf4-gqpg
Type: github-advisory

## Affected
- Hex: `rabbit_common` — affected >=3.12.0 <3.12.7
- Hex: `rabbit_common` — affected >=3.11.0 <3.11.24

## Details
### Summary

Responsibly disclosed by @NSEcho.

HTTP API did not enforce an HTTP request body limit, making it vulnerable for DoS attacks with very large messages. 

### Details

An authenticated user with sufficient credentials can publish a very large messages over the HTTP API
and cause target node to be terminated by an "out-of-memory killer"-like mechanism.

A PoC was provided to Team RabbitMQ privately.

### Impact

Denial of Service

## References
- https://github.com/rabbitmq/rabbitmq-server/security/advisories/GHSA-w6cq-9cf4-gqpg
- https://nvd.nist.gov/vuln/detail/CVE-2023-46118
- https://github.com/rabbitmq/rabbitmq-server
- https://lists.debian.org/debian-lts-announce/2023/12/msg00009.html
- https://www.debian.org/security/2023/dsa-5571
