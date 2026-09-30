# [H] LavinMQ has incomplete shovel configuration validation

## Summary
Severity: High
Advisory: CVE-2026-25767
Aliases: GHSA-wh37-6vrr-r9wg
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-12
Source: https://osv.dev/vulnerability/CVE-2026-25767
Type: osv

## Details
LavinMQ is a high-performance message queue & streaming server. Before 2.6.8, an authenticated user, with the “Policymaker” tag, could create shovels bypassing access controls. an authenticated user with the "Policymaker" management tag could exploit it to read messages from vhosts they are not authorized to access or publish messages to vhosts they are not authorized to access. This vulnerability is fixed in 2.6.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25767.json
- https://github.com/cloudamqp/lavinmq/security/advisories/GHSA-wh37-6vrr-r9wg
- https://nvd.nist.gov/vuln/detail/CVE-2026-25767
- https://github.com/cloudamqp/lavinmq/commit/3a83e5894495b60c7c32a79c3dbc9bd9fa237d9a
- https://github.com/cloudamqp/lavinmq/commit/be03da31f3db1a2552f7094ff58e953ef50cdc82
- https://github.com/cloudamqp/lavinmq/pull/1670
- https://github.com/cloudamqp/lavinmq/pull/1687
