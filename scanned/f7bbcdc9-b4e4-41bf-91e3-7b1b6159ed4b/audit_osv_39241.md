# [H] Chatwoot: SQL Injection in Conversation/Contact Filter API via Custom Attribute Values

## Summary
Severity: High
Advisory: CVE-2026-44706
Aliases: GHSA-9pgm-75gg-6948
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-44706
Type: osv

## Details
Chatwoot is a customer engagement suite. From 2.2.0 to before 4.11.2, a SQL injection vulnerability exists in the conversation and contact filter APIs. When filtering by a custom attribute of type date or number using the is_greater_than or is_less_than operators, user-supplied values in the values field of the filter payload are interpolated directly into the SQL query without parameterization. Any authenticated user with access to an account can exploit this to execute arbitrary SQL via time-based blind injection. This affects /api/v1/accounts/{account_id}/conversations/filter, /api/v1/accounts/{account_id}/contacts/filter, and /api/v1/accounts/{account_id}/custom_attribute_definitions. This vulnerability is fixed in 4.11.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44706.json
- https://github.com/chatwoot/chatwoot/security/advisories/GHSA-9pgm-75gg-6948
- https://nvd.nist.gov/vuln/detail/CVE-2026-44706
