# [M] Inconsistent Interpretation of HTTP Requests ('HTTP Request Smuggling') in Elasticsearch Leading to Information Disclosure

## Summary
Severity: Medium
Advisory: BIT-elasticsearch-2026-78605
Aliases: CVE-2026-78605
Ecosystem: Bitnami
Published: 2026-09-03
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2026-78605
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=9.5.0 <9.5.1

## Details
Inconsistent Interpretation of HTTP Requests ('HTTP Request Smuggling') (CWE-444) in Elasticsearch can lead to information disclosure via HTTP Request Smuggling (CAPEC-33). Under specific proxy deployment configurations, a network attacker could obtain confidential responses intended for other authenticated users.

## References
- https://discuss.elastic.co/t/elasticsearch-8-19-20-9-4-5-9-5-1-security-update-esa-2026-141/390092
- https://nvd.nist.gov/vuln/detail/CVE-2026-78605
