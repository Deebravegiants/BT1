# [H] Fluentd: Server-Side Request Forgery (SSRF) via Placeholder Expansion in `out_http`

## Summary
Severity: High
Advisory: BIT-fluentd-2026-44161
Aliases: CVE-2026-44161, GHSA-72f5-rr8c-r6gr
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-fluentd-2026-44161
Type: osv

## Affected
- Bitnami: `fluentd` — affected >=0 <1.19.3

## Details
Fluentd collects events from various data sources and writes them to files, RDBMS, NoSQL, IaaS, SaaS, Hadoop and so on. Prior to 1.19.3, the Fluentd out_http output plugin allows placeholders such as ${tag} in the endpoint configuration parameter, and if a placeholder value is derived from untrusted input an attacker can control the destination hostname of outbound HTTP requests and force requests to arbitrary internal services. This issue is fixed in version 1.19.3.

## References
- https://github.com/fluent/fluentd/commit/c6a01ea2e0ea01977f8d615f7c6dbfae4cba88c9
- https://github.com/fluent/fluentd/pull/5394
- https://github.com/fluent/fluentd/releases/tag/v1.19.3
- https://github.com/fluent/fluentd/security/advisories/GHSA-72f5-rr8c-r6gr
- https://nvd.nist.gov/vuln/detail/CVE-2026-44161
