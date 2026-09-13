# [M] CVE-2021-32719

## Summary
Severity: Medium
Advisory: CVE-2021-32719
Aliases: BIT-rabbitmq-2021-32719
CVSS: 4.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-06-28
Source: https://osv.dev/vulnerability/CVE-2021-32719
Type: osv

## Details
RabbitMQ is a multi-protocol messaging broker. In rabbitmq-server prior to version 3.8.18, when a federation link was displayed in the RabbitMQ management UI via the `rabbitmq_federation_management` plugin, its consumer tag was rendered without proper <script> tag sanitization. This potentially allows for JavaScript code execution in the context of the page. The user must be signed in and have elevated permissions (manage federation upstreams and policies) for this to occur. The vulnerability is patched in RabbitMQ 3.8.18. As a workaround, disable the `rabbitmq_federation_management` plugin and use [CLI tools](https://www.rabbitmq.com/cli.html) instead.

## References
- https://github.com/rabbitmq/rabbitmq-server/security/advisories/GHSA-5452-hxj4-773x
- https://github.com/rabbitmq/rabbitmq-server/pull/3122
- https://herolab.usd.de/security-advisories/usd-2021-0011/
