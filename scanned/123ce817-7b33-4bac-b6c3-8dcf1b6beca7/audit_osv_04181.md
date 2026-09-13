# [C] Appsmith: SSRF in REST API / GraphQL datasource plugins via insufficient host denylist

## Summary
Severity: Critical
Advisory: BIT-appsmith-2026-55455
Aliases: CVE-2026-55455, GHSA-m23h-pvf3-2m7p
Ecosystem: Bitnami
Published: 2026-06-29
Source: https://osv.dev/vulnerability/BIT-appsmith-2026-55455
Type: osv

## Affected
- Bitnami: `appsmith` — affected >=0 <2.1.0

## Details
Appsmith is a platform to build admin panels, internal tools, and dashboards. Prior to 2.1, the outbound HTTP host filter applied by WebClientUtils (used by the REST API and GraphQL datasource plugins) validates hosts against an exact-match string denylist. The comprehensive address-class check (loopback, any-local, link-local, fc00::/7) exists only on a separate code path used by SMTP, not by the HTTP plugin path. As a result, an authenticated user can craft outbound requests that reach loopback-bound services inside the container. This vulnerability is fixed in 2.1.

## References
- https://github.com/appsmithorg/appsmith/security/advisories/GHSA-m23h-pvf3-2m7p
- https://nvd.nist.gov/vuln/detail/CVE-2026-55455
