# [M] @hapi/wreck: Sensitive credential headers leak across cross-port and cross-scheme redirects

## Summary
Severity: Medium
Advisory: GHSA-x426-x7cc-3fpc
CVE: CVE-2026-48022
CWE: CWE-200, CWE-319, CWE-346, CWE-522, CWE-940
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-x426-x7cc-3fpc
Type: github-advisory

## Affected
- npm: `@hapi/wreck` — affected >=0 <18.1.2

## Details
### Impact
Wreck strips credential headers (Authorization, Cookie, Proxy-Authorization) before following a cross-origin redirect, but the origin check compares hostnames only and ignores scheme and port. As a result, credentials are forwarded intact across same-host port changes and HTTPS-to-HTTP downgrades, allowing a co-tenant on an adjacent port or a network-position attacker capable of forging a redirect to capture bearer tokens, session cookies, and proxy credentials and impersonate the victim against the upstream service. The fix replaces the hostname comparison with a full-origin comparison (scheme, host, and port), aligning the behavior with the WHATWG Fetch same-origin definition used by browsers.

### Patches
Upgrade to >= 18.1.2.

### Workarounds
- Set `redirects: 0` (default) and handle redirects manually with a strict origin check.
- Use the `beforeRedirect` hook to inspect the redirect target and abort or strip sensitive headers before the follow-on request.

## References
- https://github.com/hapijs/wreck/security/advisories/GHSA-x426-x7cc-3fpc
- https://github.com/hapijs/wreck/commit/b93323b63ad3adb14d2b4019d77219182211641e
- https://github.com/hapijs/wreck
