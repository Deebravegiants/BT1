# [M] Authorization Bypass Through User-Controlled Key in Kibana Leading to Unauthorized Data Modification in Kibana

## Summary
Severity: Medium
Advisory: BIT-kibana-2026-78581
Aliases: BIT-elk-2026-78581, CVE-2026-78581
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-kibana-2026-78581
Type: osv

## Affected
- Bitnami: `kibana` — affected >=8.17.0 <8.17.2

## Details
Authorization Bypass Through User-Controlled Key (CWE-639) in Kibana can lead to unauthorized data modification via Accessing Functionality Not Properly Constrained by ACLs (CAPEC-1). Under certain conditions, an authenticated user could reference another user's AI Assistant conversation identifier to access or modify a conversation they do not own. Successful exploitation requires knowledge of a hard-to-guess identifier.

## References
- https://discuss.elastic.co/t/kibana-8-16-3-8-17-2-security-update-esa-2026-51/387446
- https://nvd.nist.gov/vuln/detail/CVE-2026-78581
