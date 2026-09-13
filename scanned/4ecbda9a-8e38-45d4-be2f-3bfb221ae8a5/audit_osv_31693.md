# [C] Chatwoot has a Blind SQL-injection in Conversation and Contacts filters

## Summary
Severity: Critical
Advisory: CVE-2025-21628
Aliases: GHSA-g8f9-hh83-rcq9
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L)
Published: 2025-01-09
Source: https://osv.dev/vulnerability/CVE-2025-21628
Type: osv

## Details
Chatwoot is a customer engagement suite. Prior to 3.16.0, conversation and contact filters endpoints did not sanitize the input of query_operator passed from the frontend or the API. This provided any actor who is authenticated, an attack vector to run arbitrary SQL within the filter query by adding a tautological WHERE clause. This issue is patched with v3.16.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21628.json
- https://github.com/chatwoot/chatwoot/security/advisories/GHSA-g8f9-hh83-rcq9
- https://nvd.nist.gov/vuln/detail/CVE-2025-21628
- https://github.com/chatwoot/chatwoot/commit/b34dac7bbe3c910186083b680e51aad5ea60b44b
