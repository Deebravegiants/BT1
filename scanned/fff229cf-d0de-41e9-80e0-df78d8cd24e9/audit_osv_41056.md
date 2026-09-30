# [M] RabbitMQ management HTTP API accepts request bodies larger than configured max_http_body_size

## Summary
Severity: Medium
Advisory: CVE-2026-57212
Aliases: GHSA-5cmq-vp28-xqrj
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-57212
Type: osv

## Details
RabbitMQ is a messaging and streaming broker. Prior to 3.13.14, 4.0.19, 4.1.10, and 4.2.5, the rabbitmq_management HTTP API accepts oversized valid JSON bodies on with_decode and direct_request paths because read_complete_body checks the accumulated size before the final chunk but not the final combined size. This issue is fixed in versions 3.13.14, 4.0.19, 4.1.10, and 4.2.5.

## References
- https://github.com/rabbitmq/rabbitmq-server/releases/tag/v4.2.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57212.json
- https://github.com/rabbitmq/rabbitmq-server/security/advisories/GHSA-5cmq-vp28-xqrj
- https://nvd.nist.gov/vuln/detail/CVE-2026-57212
- https://github.com/rabbitmq/rabbitmq-server/commit/3976d148901bdfa82e1cd60b7a4534e073266ba5
- https://github.com/rabbitmq/rabbitmq-server/commit/b8fc2ef7c50a2797d15e1ea7cf34f290032303bb
- https://github.com/rabbitmq/rabbitmq-server/pull/15712
- https://github.com/rabbitmq/rabbitmq-server/pull/15714
