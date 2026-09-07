# [H] Parse Server LiveQuery subscription query depth bypass

## Summary
Severity: High
Advisory: GHSA-6qh5-m6g3-xhq6
CVE: CVE-2026-33508
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-6qh5-m6g3-xhq6
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.45
- npm: `parse-server` — affected >=0 <8.6.56

## Details
### Impact

Parse Server's LiveQuery component does not enforce the `requestComplexity.queryDepth` configuration setting when processing WebSocket subscription requests. An attacker can send a subscription with deeply nested logical operators, causing excessive recursion and CPU consumption that degrades or disrupts service availability.

Deployments are affected when the LiveQuery WebSocket endpoint is reachable by untrusted clients.

### Patches

The fix adds query condition depth validation to the LiveQuery subscription handler, enforcing the same `requestComplexity.queryDepth` limit that already protects REST API queries.

### Workarounds

There is no known workaround other than upgrading.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-6qh5-m6g3-xhq6
- https://nvd.nist.gov/vuln/detail/CVE-2026-33508
- https://github.com/parse-community/parse-server/pull/10259
- https://github.com/parse-community/parse-server/pull/10260
- https://github.com/parse-community/parse-server/commit/060d27053fb0fadf613c25aabab7fe0c82b7a899
- https://github.com/parse-community/parse-server/commit/2126fe4e12f9b399dc6b4b6a3fa70cb1825f159b
- https://github.com/parse-community/parse-server
