# [M] RabbitMQ: AMQP 1.0, AMQP 0-9-1, Stream Protocol loopback enforcement can lead to remote guest sessions due to listener-address loopback checks

## Summary
Severity: Medium
Advisory: CVE-2026-57216
Aliases: GHSA-36m6-588r-vqcw
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-57216
Type: osv

## Details
RabbitMQ is a messaging and streaming broker. Prior to 3.13.15, 4.0.20, 4.1.11, and 4.2.6, AMQP 0-9-1, AMQP 1.0, and Stream Protocol authentication can allow a loopback-restricted user such as guest to connect remotely when traffic is accepted through a trusted PROXY-protocol path and the backend listener is loopback-bound because the loopback check uses the listener-side socket address instead of the real client source. This issue is fixed in versions 3.13.15, 4.0.20, 4.1.11, and 4.2.6.

## References
- https://github.com/rabbitmq/rabbitmq-server/releases/tag/v4.2.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57216.json
- https://github.com/rabbitmq/rabbitmq-server/security/advisories/GHSA-36m6-588r-vqcw
- https://nvd.nist.gov/vuln/detail/CVE-2026-57216
- https://github.com/rabbitmq/rabbitmq-server/commit/7273c9eb6920abcde17b892dbe97ccaf906ead47
- https://github.com/rabbitmq/rabbitmq-server/commit/9f8c39fcf0acbc43080ee7017a62a02832114112
- https://github.com/rabbitmq/rabbitmq-server/pull/15936
- https://github.com/rabbitmq/rabbitmq-server/pull/15940
