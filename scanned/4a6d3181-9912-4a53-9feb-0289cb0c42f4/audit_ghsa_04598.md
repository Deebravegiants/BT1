# [H] Element Call reports full URLs of visited pages to analytics server

## Summary
Severity: High
Advisory: GHSA-6vhh-4xw6-h2h2
CVE: CVE-2026-48007
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-6vhh-4xw6-h2h2
Type: github-advisory

## Affected
- npm: `@element-hq/element-call-embedded` — affected >=0.5.17 <0.19.4

## Details
### Impact

Element Call versions 0.5.17 through 0.19.3 report analytics data to a PostHog server, when configured to by a `posthog` key in config.json or by the `posthogApiHost` and `posthogApiKey` URL parameters. Several fields of this data (`$initial_person_info`, `$session_entry_url`, and `$current_url`) were found to contain the full URL of the user's visited page, including the fragment.

Users of a standalone Element Call ‘SPA’ instance such as https://call.element.io may therefore have reported the full URLs of certain calls, including encryption passwords, to the configured PostHog server, potentially compromising the confidentiality of the calls to actors who could access both the PostHog analytics data and the encrypted media streams.

The same issue is present in Element Call's embedded package, but in practice it does not impact applications using this package (including Element Web, Element Desktop, Element X iOS, and Element X Android) because they distribute encryption keys over Matrix rather than encoding a password in the URL.

### Patches

Patched in Element Call 0.19.4.

### Workarounds

Users may opt out of analytics in the 'Feedback' tab of Element Call's settings and create new links for future calls.

Admins who host Element Call as a standalone application may disable PostHog analytics entirely by removing the `posthog` key from their deployment's config.json file.

### For more information

If there are any questions or comments about this advisory, please send an email to [security at element.io](mailto:security@element.io).

## References
- https://github.com/element-hq/element-call/security/advisories/GHSA-6vhh-4xw6-h2h2
- https://github.com/element-hq/element-call
- https://github.com/element-hq/element-call/releases/tag/v0.19.4
