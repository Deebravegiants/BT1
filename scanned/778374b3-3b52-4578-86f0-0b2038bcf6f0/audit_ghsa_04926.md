# [M] parse-server: Server option routeAllowList is bypassable through batch sub-requests

## Summary
Severity: Medium
Advisory: GHSA-p84r-h6rx-f2xr
CVE: CVE-2026-50008
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-p84r-h6rx-f2xr
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.8.0 <9.9.1-alpha.3

## Details
### Impact

The `routeAllowList` server option restricts external client access to a configured list of REST API routes. The check is only enforced as Express middleware against the outer HTTP request URL, so the `/batch` handler dispatches each sub-request to the internal router without re-running the allow-list check. An external caller whose outer route matches `batch` can issue batch sub-requests to any REST API route that the operator omitted from the allow-list.

Authentication, ACL, CLP, and other inner-route authorization controls still apply — only the operator-configured route firewall is bypassed.

### Patches

`routeAllowList` is now re-enforced for each batch sub-request inside the batch handler before dispatch, mirroring the existing per-sub-request rate-limit enforcement pattern. The path-normalization and regex-match logic was extracted into a shared helper used by both the outer middleware and the batch handler. Master and maintenance keys bypass the per-sub-request check on the same terms as the outer middleware.

### Workarounds

Operators who use `routeAllowList` and have allowlisted `batch` can mitigate without upgrading by explicitly including every inner route they intend to allow via batch in the allow-list (for example, `routeAllowList: ['batch', 'classes/Public.*', 'functions/allowedFunction']`). This approach makes those inner routes reachable as direct REST requests as well, so it is broader than the post-patch behavior, but it eliminates the bypass.

Operators who do not configure `routeAllowList` are not affected. Parse Server v8 LTS is not affected because `routeAllowList` was introduced in v9.8.0.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-p84r-h6rx-f2xr
- https://nvd.nist.gov/vuln/detail/CVE-2026-50008
- https://github.com/parse-community/parse-server/pull/10482
- https://github.com/parse-community/parse-server
