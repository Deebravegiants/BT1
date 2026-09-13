# [M] Improper Input Validation in Kibana Fleet Leading to Privilege Escalation

## Summary
Severity: Medium
Advisory: BIT-elk-2026-49095
Aliases: BIT-kibana-2026-49095, CVE-2026-49095
Ecosystem: Bitnami
Published: 2026-06-01
Source: https://osv.dev/vulnerability/BIT-elk-2026-49095
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.4.0 <9.4.2

## Details
Improper Input Validation (CWE-20) in the Kibana Fleet agent policy management feature can lead to privilege escalation. An authenticated user with Fleet management privileges can manipulate agent policy configuration by injecting values into a configuration override mechanism that is not adequately validated. An attacker can cause Elastic Agents to be issued API keys with elevated Elasticsearch privileges, potentially granting unauthorized read and write access to sensitive Elasticsearch security indices beyond what is intended for the Fleet management role.

## References
- https://discuss.elastic.co/t/kibana-fleet-8-19-16-9-3-5-and-9-4-2-security-update-esa-2026-38/386559
- https://nvd.nist.gov/vuln/detail/CVE-2026-49095
