# [M] RabbitMQ: Topic authorization can lead to cross-tenant routing-key bypass

## Summary
Severity: Medium
Advisory: CVE-2026-57217
Aliases: GHSA-gpvw-75h5-3wvx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-57217
Type: osv

## Details
RabbitMQ is a messaging and streaming broker. Prior to 3.13.15, 4.0.21, 4.1.11, and 4.2.6, RabbitMQ topic authorization can allow restricted topic writes and binds during metadata-store failures because topic-permission lookup errors from Khepri can collapse to undefined, which the internal backend treats as allow. This issue is fixed in versions 3.13.15, 4.0.21, 4.1.11, and 4.2.6.

## References
- https://github.com/rabbitmq/rabbitmq-server/releases/tag/v4.2.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57217.json
- https://github.com/rabbitmq/rabbitmq-server/security/advisories/GHSA-gpvw-75h5-3wvx
- https://nvd.nist.gov/vuln/detail/CVE-2026-57217
- https://github.com/rabbitmq/rabbitmq-server/commit/94f1d33a70fcfa09006649599e79fc92786a2d36
- https://github.com/rabbitmq/rabbitmq-server/commit/ce1f682aa6b398820c5e3ce1ff7435184027c82c
- https://github.com/rabbitmq/rabbitmq-server/pull/15941
- https://github.com/rabbitmq/rabbitmq-server/pull/15943
