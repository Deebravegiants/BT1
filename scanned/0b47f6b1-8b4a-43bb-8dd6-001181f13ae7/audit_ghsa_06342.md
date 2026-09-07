# [M] Snipe-IT: Stored DOM XSS via table selected-count IDs

## Summary
Severity: Medium
Advisory: GHSA-c8qc-wf67-342w
CVE: CVE-2026-61807
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-c8qc-wf67-342w
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.2

## Details
### Impact
The table component derives data-selected-count-id from the component $name value. On manufacturer and supplier detail pages, stored manufacturer or supplier names are passed into affected table components as that name value. The client-side JavaScript later reads the browser-decoded data-selected-count-id, uses it as a selector, and concatenates countId.substring(1) directly into an HTML string passed to jQuery .after().

Affected commit:

`b224cc636c6780386e3f73f03d1171f52ab4c37a`

Example payload for a manufacturer or supplier name:
`x[foo="><svg/onload=alert(1)>"]>`

The issue appears to involve the following flow:

Stored supplier/manufacturer name
-> table component data-selected-count-id
-> browser decodes the attribute
-> JavaScript reads countId
-> countId is used as a selector
-> countId.substring(1) is concatenated into HTML
-> jQuery .after() inserts attacker-controlled markup
-> JavaScript executes in the victim's browser

Potential impact includes arbitrary JavaScript execution in the browser of an authenticated Snipe-IT user who views the affected supplier or manufacturer detail page. If the victim has elevated privileges, this may allow access to data or actions available to that user's session.

### Patches
Patched in https://github.com/grokability/snipe-it/commit/d12ad3d53869443b96b663ba3ce2673ef343da71

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-c8qc-wf67-342w
- https://github.com/grokability/snipe-it/commit/d12ad3d53869443b96b663ba3ce2673ef343da71
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.2
