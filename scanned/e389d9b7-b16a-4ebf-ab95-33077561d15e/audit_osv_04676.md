# [H] Deserialization of Untrusted Data in Elasticsearch Leading to Remote Code Execution

## Summary
Severity: High
Advisory: BIT-elasticsearch-2026-72649
Aliases: CVE-2026-72649
Ecosystem: Bitnami
Published: 2026-09-03
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2026-72649
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=9.5.0 <9.5.1

## Details
Deserialization of Untrusted Data (CWE-502) in the Elasticsearch machine learning component can lead to remote code execution via Object Injection (CAPEC-586). A specially crafted trained model artifact could cause attacker-controlled logic to execute with a materially broader system-call surface than intended. Exploitation requires an authenticated user with sufficient privileges to create and deploy trained models.

## References
- https://discuss.elastic.co/t/elasticsearch-8-19-20-9-4-5-9-5-1-security-update-esa-2026-114/390087
- https://nvd.nist.gov/vuln/detail/CVE-2026-72649
