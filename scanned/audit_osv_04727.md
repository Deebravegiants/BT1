# [M] Missing Authorization in Kibana Leading to Unauthorized Execution of Endpoint Response Actions

## Summary
Severity: Medium
Advisory: BIT-elk-2026-72664
Aliases: BIT-kibana-2026-72664, CVE-2026-72664
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elk-2026-72664
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.0.0 <9.4.5

## Details
Missing Authorization (CWE-862) in Kibana can lead to unauthorized execution of Elastic Defend response actions on managed hosts via Accessing Functionality Not Properly Constrained by ACLs (CAPEC-1). A Kibana user who holds only detection rule authoring privileges for the Elastic Security solution can associate automated endpoint response actions with a detection rule, even though the dedicated Endpoint response action privileges that govern those capabilities (host isolation, process operations, and execute operations) have not been granted to that user. When such a rule generates alerts, the associated response actions are carried out against the matching hosts.

## References
- https://discuss.elastic.co/t/kibana-8-19-20-and-9-4-5-security-update-esa-2026-95/389527
- https://nvd.nist.gov/vuln/detail/CVE-2026-72664
