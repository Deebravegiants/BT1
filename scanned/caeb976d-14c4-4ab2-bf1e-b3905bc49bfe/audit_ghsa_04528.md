# [M] symfony/ux-autocomplete: XSS via unescaped AJAX response data

## Summary
Severity: Medium
Advisory: GHSA-mwqm-4fw3-cjvr
CVE: CVE-2026-49216
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-mwqm-4fw3-cjvr
Type: github-advisory

## Affected
- Packagist: `symfony/ux-autocomplete` — affected >=2.2.0 <2.36.0
- Packagist: `symfony/ux-autocomplete` — affected >=3.0.0 <3.1.0

## Details
### Description

The Stimulus controller shipped with `symfony/ux-autocomplete` renders AJAX response items into the dropdown by interpolating the `text` field directly into HTML template literals (`<div>${item[labelField]}</div>`) inside `_createAutocompleteWithRemoteData()`. The value is parsed as HTML rather than text, so any markup contained in the AJAX response is executed by the browser.

When the dropdown values are derived from user-supplied content, an attacker can craft a string that triggers stored XSS in the browser of any other user who later opens a page containing an autocomplete widget backed by the same data.

### Resolution

The `option` and `item` renderers used in `_createAutocompleteWithRemoteData()` now use TomSelect's `escape` helper to HTML-escape the value by default. Endpoints that legitimately return HTML (for example, to highlight the search term) can opt back in to the previous behavior by setting `options_as_html: true`. The `AutocompleteChoiceTypeExtension` normalizer that previously forced `options_as_html=false` when `autocomplete_url` was set has been dropped so the opt-in is reachable from the form layer.

The patch for this issue is available [here](https://github.com/symfony/ux/commit/842ae54bc74de389299f975f01aafae272cb0019) for branch 2.x (and forward-ported to 3.x).

### Credits

Symfony would like to thank Alex Ashkov for reporting the issue and Hugo Alliaume for providing the fix.

## References
- https://github.com/symfony/ux/security/advisories/GHSA-mwqm-4fw3-cjvr
- https://github.com/symfony/ux/commit/842ae54bc74de389299f975f01aafae272cb0019
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/ux-autocomplete/CVE-2026-49216.yaml
- https://github.com/symfony/ux
