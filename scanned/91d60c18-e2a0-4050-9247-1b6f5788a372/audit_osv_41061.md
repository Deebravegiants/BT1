# [H] RabbitMQ: Unauthenticated disclosure of OAuth client credentials via an HTTP API endpoint with certain less common OAuth 2 configurations

## Summary
Severity: High
Advisory: CVE-2026-57219
Aliases: GHSA-pj24-8j6m-vq9q
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-57219
Type: osv

## Details
RabbitMQ is a messaging and streaming broker. Prior to 3.13.15, 4.0.20, 4.1.11, and 4.2.6, the obsolete GET /api/auth endpoint can disclose the OAuth 2 client secret on RabbitMQ installations configured with management.oauth_client_secret, exposing credentials to unauthenticated callers when the management plugin and that OAuth configuration are enabled. This issue is fixed in versions 3.13.15, 4.0.20, 4.1.11, and 4.2.6.

## References
- https://github.com/rabbitmq/rabbitmq-server/releases/tag/v4.2.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57219.json
- https://github.com/rabbitmq/rabbitmq-server/security/advisories/GHSA-pj24-8j6m-vq9q
- https://nvd.nist.gov/vuln/detail/CVE-2026-57219
- https://github.com/rabbitmq/rabbitmq-server/commit/98b1daf740237c85941e8addcbea6e74f4a2743c
- https://github.com/rabbitmq/rabbitmq-server/commit/aa387c4451e7b674df3e3ba89df86a99d697cc7f
- https://github.com/rabbitmq/rabbitmq-server/pull/16083
- https://github.com/rabbitmq/rabbitmq-server/pull/16086
