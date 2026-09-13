# [M] Chatwoot: Cross-Account Resource Transfer via `account_id` Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-72719
Aliases: GHSA-x288-jh8j-348c
CVSS: 6.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72719
Type: osv

## Details
Chatwoot is a customer engagement suite. Prior to 4.9.0, Chatwoot allowed authenticated account administrators to transfer Portals, Automation Rules, Macros, and Twilio Channels to other accounts through the writable account_id parameter. This could break tenant isolation and cause cross-account data exposure, unauthorized configuration changes, or loss of access to transferred resources. This issue is fixed in version 4.9.0.

## References
- https://github.com/chatwoot/chatwoot/releases/tag/v4.9.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72719.json
- https://github.com/chatwoot/chatwoot/security/advisories/GHSA-x288-jh8j-348c
- https://nvd.nist.gov/vuln/detail/CVE-2026-72719
- https://github.com/chatwoot/chatwoot/commit/86da3f7c069f8ed6dce2576e1a760ca72b6f40fd
- https://github.com/chatwoot/chatwoot/pull/13116
