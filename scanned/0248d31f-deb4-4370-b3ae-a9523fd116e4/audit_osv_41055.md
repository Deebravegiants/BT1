# [M] RabbitMQ: UNC SSRF affecting the management UI on Windows

## Summary
Severity: Medium
Advisory: CVE-2026-57211
Aliases: GHSA-7v84-m3g5-vxq6
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-57211
Type: osv

## Details
RabbitMQ is a messaging and streaming broker. Prior to 4.1.11 and 4.2.6 on Windows, the RabbitMQ management plugin static file handler rabbit_mgmt_wm_static can pass URL-encoded backslashes to erl_prim_loader:read_file_info before path validation when multiple management extension plugins are enabled, causing outbound DNS and SMB requests to attacker-controlled UNC paths. This issue is fixed in versions 4.1.11 and 4.2.6.

## References
- https://github.com/rabbitmq/rabbitmq-server/releases/tag/v4.2.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57211.json
- https://github.com/rabbitmq/rabbitmq-server/security/advisories/GHSA-7v84-m3g5-vxq6
- https://nvd.nist.gov/vuln/detail/CVE-2026-57211
- https://github.com/rabbitmq/rabbitmq-server/commit/39c3a8e9c71da0403d8dfc13f700e60c936e3682
- https://github.com/rabbitmq/rabbitmq-server/commit/6730797f6a34b4e8308cea60adf1243857e70204
- https://github.com/rabbitmq/rabbitmq-server/pull/15803
