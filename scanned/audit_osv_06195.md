# [H] Missing Authorization in Kibana Leading to Unauthorized Execution of Host Response Actions

## Summary
Severity: High
Advisory: BIT-kibana-2026-72665
Aliases: BIT-elk-2026-72665, CVE-2026-72665
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-kibana-2026-72665
Type: osv

## Affected
- Bitnami: `kibana` — affected >=9.0.0 <9.4.5

## Details
Missing Authorization (CWE-862) in Kibana can lead to unauthorized execution of Osquery and Elastic Defend response actions on managed hosts via Accessing Functionality Not Properly Constrained by ACLs (CAPEC-1). A Kibana user who is able to author and evaluate Elastic Security detection rules can cause response actions to be carried out against enrolled agents without holding the Osquery live query privileges or the Elastic Defend response action privileges that normally govern those capabilities. Depending on the response action involved, this can result in disclosure of information from the affected hosts or in unauthorized changes to their state.

## References
- https://discuss.elastic.co/t/kibana-8-19-20-and-9-4-5-security-update-esa-2026-96/389528
- https://nvd.nist.gov/vuln/detail/CVE-2026-72665
