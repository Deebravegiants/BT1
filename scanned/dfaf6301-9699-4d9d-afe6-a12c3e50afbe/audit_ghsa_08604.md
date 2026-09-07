# [M] SillyTavern has a reflected XSS vulnerability in the CORS proxy middleware

## Summary
Severity: Medium
Advisory: GHSA-xc4x-2452-5gc9
CVE: CVE-2026-44651
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-xc4x-2452-5gc9
Type: github-advisory

## Affected
- npm: `sillytavern` — affected >=0 <1.18.0

## Details
## Resolution

Fixed in SillyTavern 1.18.0: a user-provided URL is no longer reflected in the HTTP response body.

## Overview
- Vulnerability Type: XSS
- Affected Location: `src/middleware/corsProxy.js:40`
- Trigger Scenario: reflected XSS in CORS proxy error response

## Root Cause
When `fetch(url)` throws, the code sends:
`res.status(500).send('Error occurred while trying to proxy to: ' + url + ' ' + error)`.
The `url` value is attacker-controlled (`req.params.url`) and is not HTML-escaped before rendering.

## Source-to-Sink Chain
1. Source (user-controlled input)
- Entry point: `GET /proxy/:url(*)`

2. Data flow
- Code analysis shows concrete propagation into this sink:
  - vulnerability title: `Reflected XSS in CORS proxy error response`
  - sink location reached by attacker-controlled input: `src/middleware/corsProxy.js:40`
- The same sink behavior is confirmed by controlled execution observations.

3. Sink (dangerous operation)
- Sink location: `src/middleware/corsProxy.js:40`
- Vulnerable behavior: reflected XSS in CORS proxy error response

## Exploitation Preconditions
1. The attacker can inject controllable content into a rendered response.
2. The vulnerable rendering context does not apply strict output encoding/sanitization.
3. A victim user opens the affected page or response.

## Risk
This issue enables script execution in the victim context and can compromise session or data integrity.

## Impact
An attacker may run arbitrary JavaScript in the victim context, steal tokens, and manipulate user-visible behavior.

## Remediation
1. Never concatenate raw user input into HTML error responses.
2. If URL echo is required, HTML-escape it or force plain-text output.
3. Re-enable/strengthen CSP to reduce reflected injection impact.

## References
- https://github.com/SillyTavern/SillyTavern/security/advisories/GHSA-xc4x-2452-5gc9
- https://nvd.nist.gov/vuln/detail/CVE-2026-44651
- https://github.com/SillyTavern/SillyTavern
- https://github.com/SillyTavern/SillyTavern/releases/tag/1.18.0
