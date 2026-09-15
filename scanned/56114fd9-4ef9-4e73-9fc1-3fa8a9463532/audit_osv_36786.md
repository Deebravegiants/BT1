# [M] LavinMQ is missing vhost access control

## Summary
Severity: Medium
Advisory: CVE-2026-25768
Aliases: GHSA-r2mh-8vq6-qf7m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-12
Source: https://osv.dev/vulnerability/CVE-2026-25768
Type: osv

## Details
LavinMQ is a high-performance message queue & streaming server. Before 2.6.6, an authenticated user could access metadata in the broker they should not have access to. This vulnerability is fixed in 2.6.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25768.json
- https://github.com/cloudamqp/lavinmq/security/advisories/GHSA-r2mh-8vq6-qf7m
- https://nvd.nist.gov/vuln/detail/CVE-2026-25768
- https://github.com/cloudamqp/lavinmq/commit/e871f8d0a53685f04e39e6410a2421c1f82803b0
- https://github.com/cloudamqp/lavinmq/pull/1669
