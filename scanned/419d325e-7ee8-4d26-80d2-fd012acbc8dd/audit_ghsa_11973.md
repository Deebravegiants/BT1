# [M] Parse Server has a rate limit bypass via batch request endpoint

## Summary
Severity: Medium
Advisory: GHSA-775h-3xrc-c228
CVE: CVE-2026-30972
CWE: CWE-799
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-775h-3xrc-c228
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.5.2-alpha.10
- npm: `parse-server` — affected >=0 <8.6.23

## Details
### Impact

Parse Server's rate limiting middleware is applied at the Express middleware layer, but the batch request endpoint (`/batch`) processes sub-requests internally by routing them directly through the Promise router, bypassing Express middleware including rate limiting. An attacker can bundle multiple requests targeting a rate-limited endpoint into a single batch request to circumvent the configured rate limit.

Any Parse Server deployment that relies on the built-in rate limiting feature is affected.

### Patches

The fix adds a pre-flight check in the batch request handler that counts the number of sub-requests targeting each rate-limited path and rejects the entire batch request if any path's count exceeds its configured `requestCount`.

Note that this is a server-level rate limit that counts sub-requests within a single batch request. Requests already consumed in the current time window by previous individual or batch requests are not counted against the batch, so the effective limit may be higher when combining individual and batch requests. For comprehensive rate limiting protection, use a reverse proxy or WAF.

### Workarounds

Use a reverse proxy or web application firewall (WAF) to enforce rate limiting before requests reach Parse Server.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-775h-3xrc-c228
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.10
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.23

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-775h-3xrc-c228
- https://nvd.nist.gov/vuln/detail/CVE-2026-30972
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.23
- https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.10
