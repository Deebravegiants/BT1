# [H] Server-Side Request Forgery (SSRF) in Kibana One Workflow Leading to Information Disclosure

## Summary
Severity: High
Advisory: BIT-kibana-2026-33458
Aliases: BIT-elk-2026-33458, CVE-2026-33458
Ecosystem: Bitnami
Published: 2026-04-13
Source: https://osv.dev/vulnerability/BIT-kibana-2026-33458
Type: osv

## Affected
- Bitnami: `kibana` — affected >=9.3.0 <9.3.3

## Details
Server-Side Request Forgery (CWE-918) in Kibana One Workflow can lead to information disclosure. An authenticated user with workflow creation and execution privileges can bypass host allowlist restrictions in the Workflows Execution Engine, potentially exposing sensitive internal endpoints and data.

## References
- https://discuss.elastic.co/t/kibana-9-3-3-security-update-esa-2026-28/385815
- https://nvd.nist.gov/vuln/detail/CVE-2026-33458
