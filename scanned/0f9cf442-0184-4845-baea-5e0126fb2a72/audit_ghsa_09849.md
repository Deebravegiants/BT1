# [M] follow-redirects leaks Custom Authentication Headers to Cross-Domain Redirect Targets

## Summary
Severity: Medium
Advisory: GHSA-r4q5-vmmm-2653
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-r4q5-vmmm-2653
Type: github-advisory

## Affected
- npm: `follow-redirects` — affected >=0 <1.16.0

## Details
## Summary

When an HTTP request follows a cross-domain redirect (301/302/307/308), `follow-redirects` only strips `authorization`, `proxy-authorization`, and `cookie` headers (matched by regex at index.js:469-476). Any custom authentication header (e.g., `X-API-Key`, `X-Auth-Token`, `Api-Key`, `Token`) is forwarded verbatim to the redirect target.

Since `follow-redirects` is the redirect-handling dependency for **axios** (105K+ stars), this vulnerability affects the entire axios ecosystem.

## Affected Code

`index.js`, lines 469-476:

```javascript
if (redirectUrl.protocol !== currentUrlParts.protocol &&
   redirectUrl.protocol !== "https:" ||
   redirectUrl.host !== currentHost &&
   !isSubdomain(redirectUrl.host, currentHost)) {
  removeMatchingHeaders(/^(?:(?:proxy-)?authorization|cookie)$/i, this._options.headers);
}
```

The regex only matches `authorization`, `proxy-authorization`, and `cookie`. Custom headers like `X-API-Key` are not matched.

## Attack Scenario

1. App uses axios with custom auth header: `headers: { 'X-API-Key': 'sk-live-secret123' }`
2. Server returns `302 Location: https://evil.com/steal`
3. follow-redirects sends `X-API-Key: sk-live-secret123` to `evil.com`
4. Attacker captures the API key

## Impact

Any custom auth header set via axios leaks on cross-domain redirect. Extremely common pattern. Affects all axios users in Node.js.

## Suggested Fix

Add a `sensitiveHeaders` option that users can extend, or strip ALL non-standard headers on cross-domain redirect.

## Disclosure

Source code review, manually verified. Found 2026-03-20.

## References
- https://github.com/follow-redirects/follow-redirects/security/advisories/GHSA-r4q5-vmmm-2653
- https://github.com/follow-redirects/follow-redirects/commit/844c4d302ac963d29bdb5dc1754ec7df3d70d7f9
- https://github.com/follow-redirects/follow-redirects
