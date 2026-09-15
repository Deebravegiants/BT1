# [M] Kibana Improper Authorization

## Summary
Severity: Medium
Advisory: BIT-elk-2025-68422
Aliases: BIT-kibana-2025-68422, CVE-2025-68422
Ecosystem: Bitnami
Published: 2025-12-20
Source: https://osv.dev/vulnerability/BIT-elk-2025-68422
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.2.0 <9.2.1

## Details
Improper Authorization (CWE-285) in Kibana can lead to privilege escalation (CAPEC-233) by allowing an authenticated user to bypass intended permission restrictions via a crafted HTTP request. This allows an attacker who lacks the live queries - read permission to successfully retrieve the list of live queries.

## References
- https://discuss.elastic.co/t/kibana-8-19-7-9-1-7-and-9-2-1-security-update-esa-2025-39/384187
- https://nvd.nist.gov/vuln/detail/CVE-2025-68422
