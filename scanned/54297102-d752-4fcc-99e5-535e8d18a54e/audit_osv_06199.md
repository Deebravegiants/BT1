# [H] Missing Authorization in Kibana Leading to Privilege Escalation and Information Disclosure

## Summary
Severity: High
Advisory: BIT-kibana-2026-72681
Aliases: BIT-elk-2026-72681, CVE-2026-72681
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-kibana-2026-72681
Type: osv

## Affected
- Bitnami: `kibana` — affected >=9.4.0 <9.4.4

## Details
Kibana Agent Builder does not correctly verify that the requesting user holds the privileges required by a separate Kibana feature before it creates and runs a tool that invokes that feature's functionality. This allows privilege escalation and could lead to disclosure of sensitive information that the user is not authorized to read.

## References
- https://discuss.elastic.co/t/kibana-9-4-4-security-update-esa-2026-83/389534
- https://nvd.nist.gov/vuln/detail/CVE-2026-72681
