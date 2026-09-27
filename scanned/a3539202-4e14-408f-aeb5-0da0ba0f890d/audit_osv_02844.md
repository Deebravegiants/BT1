# [M] ALPINE-CVE-2023-35789

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-35789
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-06-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-35789
Type: osv

## Affected
- Alpine:v3.20: `rabbitmq-c` — affected >=0 <0.14.0-r0
- Alpine:v3.21: `rabbitmq-c` — affected >=0 <0.14.0-r0
- Alpine:v3.22: `rabbitmq-c` — affected >=0 <0.14.0-r0
- Alpine:v3.23: `rabbitmq-c` — affected >=0 <0.14.0-r0
- Alpine:v3.24: `rabbitmq-c` — affected >=0 <0.14.0-r0

## Details
An issue was discovered in the C AMQP client library (aka rabbitmq-c) through 0.13.0 for RabbitMQ. Credentials can only be entered on the command line (e.g., for amqp-publish or amqp-consume) and are thus visible to local attackers by listing a process and its arguments.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-35789
