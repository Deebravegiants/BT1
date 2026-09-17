# [M] Improper Privilege Management in Kibana Fleet Leading to Over-Scoped Elastic Agent API Keys

## Summary
Severity: Medium
Advisory: BIT-elk-2026-72631
Aliases: BIT-kibana-2026-72631, CVE-2026-72631
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elk-2026-72631
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.5.0 <9.5.1

## Details
Improper Privilege Management (CWE-269) in Kibana Fleet can lead to privilege escalation via Privilege Escalation (CAPEC-233). An integration policy may optionally declare extra data streams that the integration writes to, which Fleet adds to the Elasticsearch API key issued to Elastic Agents enrolled in the corresponding agent policy. The resulting key allows new documents to be inserted and index mappings to be extended for specific indices. The key does not allow reading, updating, or deleting existing documents

## References
- https://discuss.elastic.co/t/kibana-9-4-5-9-5-1-security-update-esa-2026-128/389539
- https://nvd.nist.gov/vuln/detail/CVE-2026-72631
