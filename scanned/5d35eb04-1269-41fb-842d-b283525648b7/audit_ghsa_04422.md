# [H] parse-server: Denial of service via exponential-time processing of deeply nested query operators

## Summary
Severity: High
Advisory: GHSA-cgxm-vr2f-6fj8
CWE: CWE-407
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-cgxm-vr2f-6fj8
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.9.1-alpha.12
- npm: `parse-server` — affected >=0 <8.6.82

## Details
### Impact

Parse Server is vulnerable to denial of service. A remote attacker can send a single, small query (~1 KB) containing deeply nested query condition operators. Parse Server processes the nested structure with exponential time complexity, which blocks the Node.js event loop and makes the server unresponsive to all clients for the duration of processing. A single request can occupy the event loop for many seconds, and the request is repeatable. The issue affects the REST API and LiveQuery query handling and is reachable in the default configuration. Exploitation requires only the public application identifier; no user authentication is needed.

### Patches

The internal query-traversal helper that previously re-walked nested arrays — causing exponential-time processing of nested `$or`/`$and`/`$nor` operators — was corrected to traverse queries in linear time. Additionally, the optional `requestComplexity.queryDepth` limit was generalized so that nested logical operators are counted even when wrapped inside field-level operators (e.g. `$elemMatch`, `$not`) or plain field names, closing a bypass of the limit on both the REST API and LiveQuery.

### Workarounds

There is no complete configuration-only workaround on affected versions. Setting `requestComplexity.queryDepth` to a small positive integer reduces exposure but does not fully prevent the issue, because the limit can be bypassed by nesting the operators inside a field-level operator. Upgrading is strongly recommended.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-cgxm-vr2f-6fj8
- https://github.com/parse-community/parse-server/pull/10511
- https://github.com/parse-community/parse-server/pull/10512
- https://github.com/parse-community/parse-server
