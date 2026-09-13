# [H] Improper Neutralization of Special Elements Used in a Template Engine in Kibana Workflows Leading to Server-Side Request Forgery (SSRF)

## Summary
Severity: High
Advisory: BIT-kibana-2026-26938
Aliases: BIT-elk-2026-26938, CVE-2026-26938
Ecosystem: Bitnami
Published: 2026-03-03
Source: https://osv.dev/vulnerability/BIT-kibana-2026-26938
Type: osv

## Affected
- Bitnami: `kibana` — affected >=9.3.0 <9.3.1

## Details
Improper Neutralization of Special Elements Used in a Template Engine (CWE-1336) exists in Workflows in Kibana which could allow an attacker to read arbitrary files from the Kibana server filesystem, and perform Server-Side Request Forgery (SSRF) via Code Injection (CAPEC-242). This requires an authenticated user who has the workflowsManagement:executeWorkflow privilege.

## References
- https://discuss.elastic.co/t/kibana-9-3-1-security-update-esa-2026-17/385253
- https://nvd.nist.gov/vuln/detail/CVE-2026-26938
