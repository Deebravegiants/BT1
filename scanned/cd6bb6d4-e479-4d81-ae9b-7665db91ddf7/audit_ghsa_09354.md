# [M] SillyTavern has a SSRF vulnerability in the CORS proxy middleware

## Summary
Severity: Medium
Advisory: GHSA-ccfq-2454-f5xw
CVE: CVE-2026-44652
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-ccfq-2454-f5xw
Type: github-advisory

## Affected
- npm: `sillytavern` — affected >=0 <1.18.0

## Details
## Resolution

SillyTavern 1.18.0 added a generic server-side request filter (Private Request Whitelisting). Since we expect users to use the application in a trusted environment, the filter is disabled by default, however it is strongly advised to be enabled and properly configured when an instance is being hosted over a network, as suggested by a console warning message and an officially published security checklist for administrators.

Documentation: 

- https://docs.sillytavern.app/administration/config-yaml/#private-address-whitelisting
- https://docs.sillytavern.app/administration/#security-checklist

## Note on future SSRF findings

Since the request filter applies to the entire application, no SSRF vulnerabilities against individual endpoints will be accepted, unless it has been proven that a properly configured and enabled filter can be bypassed in an undocumented way. Only advisories disclosed before the 1.18.0 release will be posted if their concern is SSRF.

## Overview
- Vulnerability Type: SSRF
- Affected Location: `src/middleware/corsProxy.js:31`
- Trigger Scenario: SSRF in optional CORS proxy

## Root Cause
`corsProxyMiddleware` forwards `req.params.url` directly into `fetch(url, ...)`. It only blocks circular requests to its own host and does not enforce destination allowlist or private/loopback restrictions, enabling SSRF.

## Source-to-Sink Chain
1. Source (user-controlled input)
- Entry point: `GET /proxy/:url(*)`

2. Data flow
- Code analysis shows concrete propagation into this sink:
  - vulnerability title: `SSRF in optional CORS proxy`
  - sink location reached by attacker-controlled input: `src/middleware/corsProxy.js:31`
- The same sink behavior is confirmed by controlled execution observations.

3. Sink (dangerous operation)
- Sink location: `src/middleware/corsProxy.js:31`
- Vulnerable behavior: SSRF in optional CORS proxy

## Exploitation Preconditions
1. The attacker can control or influence a URL/endpoint parameter.
2. The server can access internal or sensitive network targets.
3. Outbound request validation or redirect controls are insufficient.

## Risk
This issue can be used to pivot network access and reach unintended internal resources.

## Impact
An attacker may access internal network services or metadata endpoints and exfiltrate sensitive responses.

## Remediation
1. Enforce strict destination allowlist for proxy targets.
2. Block loopback, link-local, RFC1918, and metadata address ranges.
3. Apply the same destination validation to redirects.

## References
- https://github.com/SillyTavern/SillyTavern/security/advisories/GHSA-ccfq-2454-f5xw
- https://nvd.nist.gov/vuln/detail/CVE-2026-44652
- https://github.com/SillyTavern/SillyTavern
- https://github.com/SillyTavern/SillyTavern/releases/tag/1.18.0
