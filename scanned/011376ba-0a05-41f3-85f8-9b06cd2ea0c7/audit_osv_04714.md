# [M] Improper Access Control in Kibana Leading to Unauthorized Data Modification and Information Disclosure

## Summary
Severity: Medium
Advisory: BIT-elk-2026-56146
Aliases: BIT-kibana-2026-56146, CVE-2026-56146
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-elk-2026-56146
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.4.0 <9.4.3

## Details
Improper Access Control (CWE-284) in Kibana can lead to unauthorized modification of Entity Analytics Watchlist configuration and potential information disclosure. A low-privileged authenticated user with read-only Security Solution access could perform write operations on watchlist data that should require elevated privileges. Under specific deployment conditions, this could also allow such a user to access data beyond their authorized scope.

## References
- https://discuss.elastic.co/t/kibana-9-4-3-security-update-esa-2026-58/388557
- https://nvd.nist.gov/vuln/detail/CVE-2026-56146
