# [M] Kibana Improper Authorization

## Summary
Severity: Medium
Advisory: BIT-elk-2025-68386
Aliases: BIT-kibana-2025-68386, CVE-2025-68386
Ecosystem: Bitnami
Published: 2025-12-20
Source: https://osv.dev/vulnerability/BIT-elk-2025-68386
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.2.0 <9.2.2

## Details
Improper Authorization (CWE-285) in Kibana can lead to privilege escalation (CAPEC-233) by allowing an authenticated user to change a document's sharing type to "global," even though they do not have permission to do so, making it visible to everyone in the space via a crafted a HTTP request.

## References
- https://discuss.elastic.co/t/kibana-8-19-8-9-1-8-and-9-2-2-security-update-esa-2025-38/384186
- https://nvd.nist.gov/vuln/detail/CVE-2025-68386
