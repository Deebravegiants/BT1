# [M] Improper Control of Generation of Code in Kibana Leading to Privilege Escalation

## Summary
Severity: Medium
Advisory: BIT-elk-2026-78593
Aliases: BIT-kibana-2026-78593, CVE-2026-78593
Ecosystem: Bitnami
Published: 2026-09-09
Source: https://osv.dev/vulnerability/BIT-elk-2026-78593
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.5.0 <9.5.3

## Details
An insufficiently validated configuration field in Kibana's Cribl integration allows an authenticated user holding Kibana Fleet management privileges to inject attacker-controlled expressions into a server-side script template, resulting in an Elasticsearch ingest pipeline being written beyond the caller's authorized Elasticsearch permissions.

## References
- https://discuss.elastic.co/t/kibana-8-19-21-9-4-6-9-5-3-security-update-esa-2026-151/390159
- https://nvd.nist.gov/vuln/detail/CVE-2026-78593
