# [M] Authorization Bypass Through User-Controlled Key in Kibana Leading to Unauthorized Query Execution on Managed Hosts

## Summary
Severity: Medium
Advisory: BIT-elk-2026-72666
Aliases: BIT-kibana-2026-72666, CVE-2026-72666
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elk-2026-72666
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.1.0 <9.4.5

## Details
Authorization Bypass Through User-Controlled Key (CWE-639) in Kibana can lead to unauthorized query execution against Elastic Agents that are assigned to a Kibana space the requesting user has no access to, via Accessing Functionality Not Properly Constrained by ACLs (CAPEC-1). A user who is authorized to run Osquery live queries in one space can have a query carried out on hosts belonging to another space, resulting in disclosure of information from those hosts to the Osquery results data stream.

## References
- https://discuss.elastic.co/t/kibana-9-4-5-security-update-esa-2026-97/389537
- https://nvd.nist.gov/vuln/detail/CVE-2026-72666
