# [M] Incorrect Authorization in Kibana Leading to Unauthorized Disabling of Privilege Monitoring

## Summary
Severity: Medium
Advisory: BIT-elk-2026-72633
Aliases: BIT-kibana-2026-72633, CVE-2026-72633
Ecosystem: Bitnami
Published: 2026-09-07
Source: https://osv.dev/vulnerability/BIT-elk-2026-72633
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.5.0 <9.5.2

## Details
Incorrect Authorization (CWE-863) in Kibana Entity Analytics can lead to a loss of security monitoring via Accessing Functionality Not Properly Constrained by ACLs (CAPEC-1). An authenticated user holding only read-level Security feature access, and no Elasticsearch privileges, could stop the recurring Privilege Monitoring engine task for a Kibana space. Privileged user monitoring then stops producing data for that space while the engine continues to report a healthy state to operators.

## References
- https://discuss.elastic.co/t/kibana-9-4-6-9-5-2-security-update-esa-2026-130/390059
- https://nvd.nist.gov/vuln/detail/CVE-2026-72633
