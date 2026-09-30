# [H] OpenClaw affected by cross-site request forgery (CSRF) through loopback browser mutation endpoints

## Summary
Severity: High
Advisory: GHSA-3fqr-4cg8-h96q
CVE: CVE-2026-26317
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-3fqr-4cg8-h96q
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14
- npm: `clawdbot` — affected >=0

## Details
## Summary
Browser-facing localhost mutation routes accepted cross-origin browser requests without explicit Origin/Referer validation. Loopback binding reduces remote exposure but does not prevent browser-initiated requests from malicious origins.

## Impact
A malicious website can trigger unauthorized state changes against a victim's local OpenClaw browser control plane (for example opening tabs, starting/stopping the browser, mutating storage/cookies) if the browser control service is reachable on loopback in the victim's browser context.

## Affected Packages / Versions
- openclaw (npm): <= 2026.2.13
- clawdbot (npm): <= 2026.1.24-3

## Details
The browser control servers bind to loopback but exposed mutating HTTP endpoints without a CSRF-style guard. Browsers may send cross-origin requests to loopback addresses; without explicit validation, state-changing operations could be triggered from a non-loopback Origin/Referer.

## Fix
Mutating HTTP methods (POST/PUT/PATCH/DELETE) are rejected when the request indicates a non-loopback Origin/Referer (or `Sec-Fetch-Site: cross-site`).

## Fix Commit(s)
- openclaw/openclaw: b566b09f81e2b704bf9398d8d97d5f7a90aa94c3

## Workarounds / Mitigations
- Enable browser control auth (token/password) and avoid running with auth disabled.
- Upgrade to a release that includes the fix.

## Credits
- Reporter: @vincentkoc

## Release Process Note
`patched_versions` is set to the planned next release version. Once that npm release is published, the advisory should be ready to publish with no further edits.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3fqr-4cg8-h96q
- https://nvd.nist.gov/vuln/detail/CVE-2026-26317
- https://github.com/openclaw/openclaw/commit/b566b09f81e2b704bf9398d8d97d5f7a90aa94c3
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
