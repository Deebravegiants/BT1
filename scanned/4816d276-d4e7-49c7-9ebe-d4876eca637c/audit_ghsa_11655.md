# [H] Parse Server: Denial of Service via unindexed database query for unconfigured auth providers

## Summary
Severity: High
Advisory: GHSA-g4cf-xj29-wqqr
CVE: CVE-2026-33538
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-g4cf-xj29-wqqr
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.52
- npm: `parse-server` — affected >=0 <8.6.58

## Details
### Impact

An unauthenticated attacker can cause Denial of Service by sending authentication requests with arbitrary, unconfigured provider names. The server executes a database query for each unconfigured provider before rejecting the request, and since no database index exists for unconfigured providers, each request triggers a full collection scan on the user database. This can be parallelized to saturate database resources.

### Patches

The fix validates that an authentication provider is configured before executing any database query. Requests with unconfigured providers are now rejected immediately without querying the database.

### Workarounds

There is no known workaround other than upgrading.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-g4cf-xj29-wqqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-33538
- https://github.com/parse-community/parse-server/pull/10270
- https://github.com/parse-community/parse-server/pull/10271
- https://github.com/parse-community/parse-server/commit/40eb442e02672986730007d0a1edb22c1c4bd357
- https://github.com/parse-community/parse-server/commit/fbac847499e57f243315c5fc7135be1d58bb8e54
- https://github.com/parse-community/parse-server
