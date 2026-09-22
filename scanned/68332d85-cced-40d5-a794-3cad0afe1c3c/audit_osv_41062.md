# [H] RabbitMQ: Stream listener does not enforce configured frame-size limit during authentication, permitting unauth'd mem-exhaust DoS

## Summary
Severity: High
Advisory: CVE-2026-57220
Aliases: GHSA-f364-87q5-j35q
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-57220
Type: osv

## Details
RabbitMQ is a messaging and streaming broker. Prior to 4.2.6, the RabbitMQ stream listener does not enforce the configured stream frame-size limit while assembling frames during authentication and before Tune negotiation, allowing an unauthenticated remote client to declare oversized frame lengths and consume broker memory in rabbit_stream_core. This issue is fixed in version 4.2.6.

## References
- https://github.com/rabbitmq/rabbitmq-server/releases/tag/v4.2.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57220.json
- https://github.com/rabbitmq/rabbitmq-server/security/advisories/GHSA-f364-87q5-j35q
- https://nvd.nist.gov/vuln/detail/CVE-2026-57220
- https://github.com/rabbitmq/rabbitmq-server/commit/595ec28fa1621b1f2c28124e4e0466a8ad963547
- https://github.com/rabbitmq/rabbitmq-server/commit/773a49c4921e8be990262a2d609c35916825679e
- https://github.com/rabbitmq/rabbitmq-server/pull/16171
- https://github.com/rabbitmq/rabbitmq-server/pull/16173
