# [M] OpenClaw affected by SSRF in optional Tlon (Urbit) extension authentication

## Summary
Severity: Medium
Advisory: GHSA-pg2v-8xwh-qhcc
CVE: CVE-2026-28476
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-pg2v-8xwh-qhcc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
## Summary
The optional Tlon (Urbit) extension previously accepted a user-provided base URL for authentication and used it to construct an outbound HTTP request, enabling server-side request forgery (SSRF) in affected deployments.

## Impact
This only affects deployments that have installed and configured the Tlon (Urbit) extension, and where an attacker can influence the configured Urbit URL. Under those conditions, the gateway could be induced to make HTTP requests to attacker-chosen hosts (including internal addresses).

Deployments that do not use the Tlon extension, or where untrusted users cannot change the Urbit URL, are not impacted.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.13`

## Fixed Versions
- `2026.2.14` (planned next release)

## Fix Commit(s)
- `bfa7d21e997baa8e3437657d59b1e296815cc1b1`

## Details
Urbit authentication now validates and normalizes the base URL and uses an SSRF guard that blocks private/internal hosts by default (opt-in: `channels.tlon.allowPrivateNetwork`).

## Release Process Note
This advisory is pre-populated with the planned patched version (`2026.2.14`). After `openclaw@2026.2.14` is published to npm, publish this advisory without further edits.

Thanks @p80n-sec for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-pg2v-8xwh-qhcc
- https://nvd.nist.gov/vuln/detail/CVE-2026-28476
- https://github.com/openclaw/openclaw/commit/bfa7d21e997baa8e3437657d59b1e296815cc1b1
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
- https://www.vulncheck.com/advisories/openclaw-server-side-request-forgery-in-tlon-extension-authentication
