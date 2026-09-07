# [M] srvx is vulnerable to middleware bypass via absolute URI in request line 

## Summary
Severity: Medium
Advisory: GHSA-p36q-q72m-gchr
CVE: CVE-2026-33732
CWE: CWE-706
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-p36q-q72m-gchr
Type: github-advisory

## Affected
- npm: `srvx` — affected >=0 <0.11.13

## Details
## Summary

A pathname parsing discrepancy in srvx's `FastURL` allows middleware bypass on the Node.js adapter when a raw HTTP request uses an absolute URI with a non-standard scheme (e.g. `file://`).

## Details

When Node.js receives an absolute URI in the request line (e.g. `GET file://hehe?/internal/run HTTP/1.1`), `req.url` is set verbatim to `file://hehe?/internal/run`. Since this doesn't start with `/`, `NodeRequestURL` passes it directly to `FastURL` as a string, which stores it in `#href` for lazy manual parsing.

`FastURL#getPos()` locates the pathname by finding `://` then scanning for the next `/` — but this fails for URLs like `file://hehe?/internal/run` where a `?` appears before the first `/` after the authority. The manual parser extracts pathname as `/internal/run`, while native `URL` correctly parses it as pathname `/` with search `?/internal/run`.

This discrepancy means the router (using the fast-path) matches `/internal/run`, but if any middleware triggers a deopt to native `URL` (e.g. by accessing `hostname`), subsequent middleware sees a different pathname — bypassing route-based middleware guards.

This is a bypass of [CVE-2026-33131](https://github.com/h3js/h3/security/advisories/GHSA-3vj8-jmxq-cgj5).

## Impact

Route-based middleware (auth guards, rate limiters, etc.) can be bypassed on the Node.js adapter when a prior middleware triggers `FastURL` deopt. Requires sending a raw HTTP request (not possible from browsers).

## Fix

srvx `FastURL` constructor now deopts to native `URL` for any string not starting with `/`, ensuring consistent pathname resolution.

## References
- https://github.com/h3js/h3/security/advisories/GHSA-p36q-q72m-gchr
- https://nvd.nist.gov/vuln/detail/CVE-2026-33732
- https://github.com/h3js/srvx/commit/de0d69901c357f36a39b7e13eebef6c930652baa
- https://github.com/h3js/srvx
- https://github.com/h3js/srvx/releases/tag/v0.11.13
