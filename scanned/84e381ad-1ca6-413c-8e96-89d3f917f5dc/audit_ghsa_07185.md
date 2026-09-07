# [M] React Router: RSCErrorHandler Missing Protocol Validation (XSS)

## Summary
Severity: Medium
Advisory: GHSA-h8fp-f39c-q6mh
CVE: CVE-2026-53667
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-h8fp-f39c-q6mh
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.11.0 <7.18.0

## Details
This is a follow up to https://github.com/remix-run/react-router/security/advisories/GHSA-8646-j5j9-6r62.  React Router was alerted of a code path in the (unstable) RSC error handling path in which redirects from untrusted sources could still result in an XSS vector via attacker-supplied redirect targets

> [!NOTE]
> This only affects your application if you are using the unstable RSC APIs

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-h8fp-f39c-q6mh
- https://github.com/remix-run/react-router/pull/15177
- https://github.com/remix-run/react-router/commit/ce596e823f0d7b883a433af1d5a839a8b9fe0242
- https://github.com/remix-run/react-router
- https://github.com/remix-run/react-router/blob/main/CHANGELOG.md#v7180
- https://github.com/remix-run/react-router/releases/tag/react-router@7.18.0
