# [M] CVE-2021-32718

## Summary
Severity: Medium
Advisory: CVE-2021-32718
Aliases: BIT-rabbitmq-2021-32718, GHSA-c3hj-rg5h-2772
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-06-28
Source: https://osv.dev/vulnerability/CVE-2021-32718
Type: osv

## Details
RabbitMQ is a multi-protocol messaging broker. In rabbitmq-server prior to version 3.8.17, a new user being added via management UI could lead to the user's bane being rendered in a confirmation message without proper `<script>` tag sanitization, potentially allowing for JavaScript code execution in the context of the page. In order for this to occur, the user must be signed in and have elevated permissions (other user management). The vulnerability is patched in RabbitMQ 3.8.17. As a workaround, disable `rabbitmq_management` plugin and use CLI tools for management operations and Prometheus and Grafana for metrics and monitoring.

## References
- https://github.com/rabbitmq/rabbitmq-server/security/advisories/GHSA-c3hj-rg5h-2772
- https://github.com/rabbitmq/rabbitmq-server/pull/3028
- http://seclists.org/fulldisclosure/2021/Dec/3
