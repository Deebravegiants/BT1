# [M] Content Injection via TileJSON attribute in mapbox.js

## Summary
Severity: Medium
Advisory: GHSA-qr28-7j6p-9hmv
CVE: CVE-2017-1000042
CWE: CWE-79
Ecosystem: RubyGems, npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-qr28-7j6p-9hmv
Type: github-advisory

## Affected
- npm: `mapbox.js` — affected >=0 <1.6.5
- npm: `mapbox.js` — affected >=2.0.0 <2.1.7
- RubyGems: `mapbox-rails` — affected >=1.0.0 <1.6.5
- RubyGems: `mapbox-rails` — affected >=2.0.0 <2.1.7

## Details
Versions 1.x prior to 1.6.5 and 2.x prior to 2.1.7 of `mapbox.js` are vulnerable to a cross-site-scripting attack in certain uncommon usage scenarios.

If `L.mapbox.map` or `L.mapbox.tileLayer` are used to load untrusted TileJSON content from a non-Mapbox URL, it is possible for a malicious user with control over the TileJSON content to inject script content into the "attribution" value of the TileJSON which will be executed in the context of the page using Mapbox.js.



## Recommendation

Version 2.x: Update to version 2.1.7 or later.
Version 1.x: Update to version 1.6.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000042
- https://hackerone.com/reports/54327
- https://github.com/advisories/GHSA-qr28-7j6p-9hmv
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/mapbox-rails/CVE-2017-1000042.yml
- https://nodesecurity.io/advisories/49
- https://www.npmjs.com/advisories/49
