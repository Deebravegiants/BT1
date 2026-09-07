# [H] parse-server has GraphQL complexity validator exponential fragment traversal DoS

## Summary
Severity: High
Advisory: GHSA-mfj6-6p54-m98c
CVE: CVE-2026-34573
CWE: CWE-407
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-mfj6-6p54-m98c
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.7.0-alpha.12
- npm: `parse-server` — affected >=0 <8.6.68

## Details
### Impact

The GraphQL query complexity validator can be exploited to cause a denial-of-service by sending a crafted query with binary fan-out fragment spreads. A single unauthenticated request can block the Node.js event loop for seconds, denying service to all concurrent users. This only affects deployments that have enabled the `requestComplexity.graphQLDepth` or `requestComplexity.graphQLFields` configuration options.

### Patches

The fix replaces the per-branch fragment traversal with memoized fragment computation, reducing the traversal from exponential O(2^N) to linear O(N) time. Additionally, early termination aborts the traversal as soon as configured limits are exceeded.

### Workarounds

Disable GraphQL complexity limits by setting `requestComplexity.graphQLDepth` and `requestComplexity.graphQLFields` to `-1` (the default).

### Resources

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-mfj6-6p54-m98c
- Fix Parse Server 9: https://github.com/parse-community/parse-server/pull/10344
- Fix Parse Server 8: https://github.com/parse-community/parse-server/pull/10345

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-mfj6-6p54-m98c
- https://nvd.nist.gov/vuln/detail/CVE-2026-34573
- https://github.com/parse-community/parse-server/pull/10344
- https://github.com/parse-community/parse-server/pull/10345
- https://github.com/parse-community/parse-server/commit/ea15412795f34594cc8a674fe858d445675e0295
- https://github.com/parse-community/parse-server/commit/f759bda075298ec44e2b4fb57659a0c56620483b
- https://github.com/parse-community/parse-server
