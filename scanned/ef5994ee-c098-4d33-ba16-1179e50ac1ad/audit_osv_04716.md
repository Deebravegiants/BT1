# [M] Missing Authorization in Kibana Leading to Unauthorized Access to Cloud Connect Management Functions

## Summary
Severity: Medium
Advisory: BIT-elk-2026-63141
Aliases: BIT-kibana-2026-63141, CVE-2026-63141
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-elk-2026-63141
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.4.0 <9.4.4

## Details
Missing Authorization (CWE-862) in Kibana allows an authenticated user to access and modify Cloud Connect configuration and service settings without the required feature privileges, via direct requests to insufficiently protected product endpoints.

## References
- https://discuss.elastic.co/t/kibana-9-3-8-9-4-4-security-update-esa-2026-65/388566
- https://nvd.nist.gov/vuln/detail/CVE-2026-63141
