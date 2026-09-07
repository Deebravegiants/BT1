# [H] TinaCMS: Cross-origin postMessage handlers and rich-text URL-sanitization bypass enable stored XSS and session takeover

## Summary
Severity: High
Advisory: GHSA-g5qx-h5f3-mp2f
CVE: CVE-2026-55660
CWE: CWE-346, CWE-601, CWE-79, CWE-940
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-g5qx-h5f3-mp2f
Type: github-advisory

## Affected
- npm: `tinacms` — affected >=0 <3.9.3
- npm: `@tinacms/app` — affected >=0 <2.5.6

## Details
TinaCMS registers window message listeners — the useTina overlay handler, the OAuth authentication popup handler, and the admin↔preview iframe GraphQL reducer — that act on event.data without verifying event.origin or event.source, and post messages using non-specific target origins. A page the victim visits (or a window in an opener/iframe relationship with a Tina admin) can forge messages to drive the editor, inject preview content, or observe/forge the OAuth popup channel to take over an authenticated editing session.

Fixed in [#7056](https://github.com/tinacms/tinacms/pull/7056) by allow-listing trusted origins and verifying event.source (isFromAdmin, isFromTrustedPreviewOrigin), and by posting only to explicit target origins (never "*").

Note: the rich-text URL-sanitization issue previously bundled here has been split into its own advisory (GHSA-2vcc-5v34-9jc8) so each vulnerability can receive a distinct CVE.

## References
- https://github.com/tinacms/tinacms/security/advisories/GHSA-g5qx-h5f3-mp2f
- https://github.com/tinacms/tinacms/pull/7056
- https://github.com/tinacms/tinacms
