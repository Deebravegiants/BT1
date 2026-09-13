# [H] Relative Path Traversal in Kibana Fleet Leading to Unauthorized Deletion of Users and Other Resources

## Summary
Severity: High
Advisory: BIT-elk-2026-72677
Aliases: BIT-kibana-2026-72677, CVE-2026-72677
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elk-2026-72677
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.4.0 <9.4.3

## Details
Relative Path Traversal (CWE-23) in Kibana can lead to the unauthorized deletion of Kibana resources via Relative Path Traversal (CAPEC-139). Kibana Fleet accepted a user-supplied identifier for a Fleet Server host configuration without rejecting relative traversal sequences. The identifier is stored as provided and is later incorporated into the request that Kibana issues when that configuration is removed.

## References
- https://discuss.elastic.co/t/kibana-8-19-17-9-3-6-9-4-3-security-update-esa-2026-94/389512
- https://nvd.nist.gov/vuln/detail/CVE-2026-72677
