# [M] Cross-tenant subscription disclosure in AshGraphql authorizes notifications in memory without a tenant-scoped read

## Summary
Severity: Medium
Advisory: CVE-2026-80223
Aliases: EEF-CVE-2026-80223, GHSA-rcqc-59g2-gjg2
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-80223
Type: osv

## Details
Incorrect Authorization vulnerability in ash-project ash_graphql allows an authenticated subscriber in one tenant to receive another tenant's records over GraphQL subscriptions.

The subscription resolver in AshGraphql.Graphql.Resolver authorizes each notification payload in memory: its fast path calls Ash.can/3 with run_queries?: false, which evaluates the read policy filter against the in-memory record via Ash.Expr.eval/2 and never issues a query. Ash applies multitenancy at query-build and data-layer-prefix time, not inside query.filter, so the evaluated policy carries no tenant condition and a tenant-B notification routed to a tenant-A subscriber is emitted whenever the policy filter is true. The single-notification clause has no tenant guard at all, and the batched clause checks only the head of the notification list, so non-head entries authorize purely in memory. A tenant-scoped read is reached only when filter evaluation fails.

This issue affects ash_graphql: from 1.4.0 before 1.11.0.

## References
- https://cna.erlef.org/cves/CVE-2026-80223.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-80223
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80223.json
- https://github.com/ash-project/ash_graphql/security/advisories/GHSA-rcqc-59g2-gjg2
- https://nvd.nist.gov/vuln/detail/CVE-2026-80223
- https://github.com/ash-project/ash_graphql/commit/6e30b8b5a04bdeaed5d7514caa6b2d056d8d993e
- https://github.com/ash-project/ash_graphql
