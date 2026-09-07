# [M] Gem in a Box vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-98hq-3qvg-pg78
CVE: CVE-2017-14506
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-98hq-3qvg-pg78
Type: github-advisory

## Affected
- RubyGems: `geminabox` — affected >=0 <0.13.6

## Details
geminabox (aka Gem in a Box) before 0.13.6 is vulnerable to Cross-site Scripting (XSS), as demonstrated by uploading a gem file that has a crafted gem.homepage value in its .gemspec file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14506
- https://github.com/geminabox/geminabox/commit/99aaae196c4fc6ae0df28e186ca1e493ae658e02
- https://github.com/geminabox/geminabox
- https://github.com/geminabox/geminabox/blob/master/CHANGELOG.md
- http://baraktawily.blogspot.co.il/2017/09/gem-in-box-xss-vulenrability-cve-2017.html
