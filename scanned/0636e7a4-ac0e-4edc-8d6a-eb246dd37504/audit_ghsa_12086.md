# [M] Parse Server email verification resend page leaks user existence

## Summary
Severity: Medium
Advisory: GHSA-h29g-q5c2-9h4f
CVE: CVE-2026-33323
CWE: CWE-204
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-h29g-q5c2-9h4f
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.40
- npm: `parse-server` — affected >=0 <8.6.51

## Details
### Impact

The Pages route and legacy PublicAPI route for resending email verification links return distinguishable responses depending on whether the provided username exists and has an unverified email. This allows an unauthenticated attacker to enumerate valid usernames by observing different redirect targets. The existing `emailVerifySuccessOnInvalidEmail` configuration option, which is enabled by default and protects the API route against this, did not apply to these routes.

### Patches

The email verification resend routes now respect the `emailVerifySuccessOnInvalidEmail` option. When set to `true` (the default), both routes redirect to the success page regardless of the outcome, preventing user enumeration.

### Workarounds

There is no known workaround to prevent the information disclosure other than upgrading.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-h29g-q5c2-9h4f
- https://nvd.nist.gov/vuln/detail/CVE-2026-33323
- https://github.com/parse-community/parse-server/pull/10238
- https://github.com/parse-community/parse-server/pull/10243
- https://github.com/parse-community/parse-server/commit/967aa57732202009b2389ce9ecb3130d53d657e5
- https://github.com/parse-community/parse-server/commit/fbda4cb0c5cbc8fad08a216823b6b64d4ae289c3
- https://github.com/parse-community/parse-server
