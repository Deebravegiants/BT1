# [M] NocoDB Missing Ownership Validation in MCP Token Operations

## Summary
Severity: Medium
Advisory: GHSA-p9x3-w98f-7j3q
CVE: CVE-2026-28361
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-p9x3-w98f-7j3q
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <0.301.3

## Details
### Summary
The MCP token service did not validate token ownership, allowing a Creator within the same base to read, regenerate, or delete another user's MCP tokens if the token ID was known.

### Details
`McpTokenService.get()`, `regenerateToken()`, and `delete()` did not filter by `fk_user_id`. The analogous `ApiTokensService` correctly enforced ownership.

### Impact
Limited — requires Creator role and knowledge of target token ID. Primary risk is denial of service (invalidating tokens) and scoped token disclosure.

### Credit
This issue was reported by [@bugbunny-research](https://github.com/bugbunny-research) (bugbunny.ai).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-p9x3-w98f-7j3q
- https://nvd.nist.gov/vuln/detail/CVE-2026-28361
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/0.301.3
