# [H] Path Traversal in Kibana Leading to Unauthorized Deletion of User Accounts

## Summary
Severity: High
Advisory: BIT-elk-2026-33462
Aliases: BIT-kibana-2026-33462, CVE-2026-33462
Ecosystem: Bitnami
Published: 2026-06-01
Source: https://osv.dev/vulnerability/BIT-elk-2026-33462
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.0.0 <9.3.5

## Details
A path traversal vulnerability was identified in Kibana's dashboard management functionality. An authenticated user with limited permissions could create a dashboard with a specially crafted identifier. When an administrator subsequently attempts to delete this dashboard through the Kibana interface, the deletion request is redirected to an unintended internal endpoint, potentially resulting in the unauthorized deletion of user accounts or other resources. Exploitation requires an administrator to perform a delete action on the maliciously crafted dashboard object.

## References
- https://discuss.elastic.co/t/kibana-8-19-16-and-9-3-5-security-update-esa-2026-30/386545
- https://nvd.nist.gov/vuln/detail/CVE-2026-33462
