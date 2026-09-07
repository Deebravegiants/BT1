# [H] mediawiki/maps has stored XSS through the overlays parameter in the display_map parser function

## Summary
Severity: High
Advisory: GHSA-4h7g-5542-v3fc
CVE: CVE-2026-52854
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-4h7g-5542-v3fc
Type: github-advisory

## Affected
- Packagist: `mediawiki/maps` — affected >=0 <12.1.3

## Details
### Summary
Stored XSS through wikitext can be performed by inserting malicious HTML into the `overlays` parameter of the `display_map` parser function when using the leaflet service.

### Details
The maps extension doesn't escape overlay names before passing them to leaflet.
Leaflet then inserts them as HTML: https://github.com/ProfessionalWiki/Maps/blob/ca5139fabd75f3c34f47ea3fd161306506b053bc/resources/lib/leaflet/leaflet.js#L5243

### PoC
Preview the following wikitext, using the default configuration options of the extension:
```
{{#display_map:0,0|service=leaflet|overlays=OpenTopoMap.<img src=x onerror="alert(1);">}}
```

### Impact
Stored XSS can be performed by any user with the `edit` permission.

## References
- https://github.com/ProfessionalWiki/Maps/security/advisories/GHSA-4h7g-5542-v3fc
- https://github.com/ProfessionalWiki/Maps
